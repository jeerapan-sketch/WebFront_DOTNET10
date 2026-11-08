pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    parameters {
        string(
            name: 'TARGET_URL',
            defaultValue: 'http://accessflow-web-dev.10.80.1.101.sslip.io/login',
            description: 'DEV Web login URL. Browser login and /permissions coverage use this same origin; use http://accessflow-web-dev.10.80.1.101.sslip.io/login.'
        )
        string(
            name: 'API_SPEC_URL',
            defaultValue: 'http://webimportexcel-dev.10.80.1.101.sslip.io/swagger/v1/swagger.json',
            description: 'WebImportExcel OpenAPI/Swagger JSON URL for the ZAP API scan'
        )
        string(
            name: 'AUTH_LOGIN_URL',
            defaultValue: 'http://webimportexcel-dev.10.80.1.101.sslip.io/api/auth/login',
            description: 'Backend login endpoint used to obtain an access token for authorized API scanning'
        )
        choice(
            name: 'SCAN_MODE',
            choices: ['REPORT_ONLY', 'ENFORCE_RULES'],
            description: 'REPORT_ONLY keeps warnings from failing the build. ENFORCE_RULES applies zap-rules.conf.'
        )
        string(
            name: 'SPIDER_MINUTES',
            defaultValue: '3',
            description: 'Maximum number of minutes for the ZAP spider'
        )
    }

    environment {
        ZAP_IMAGE = 'ghcr.io/zaproxy/zaproxy:stable'
        ZAP_WEB_IMAGE = 'accessflow-zap-browser:local'
        ZAP_REPORT_DIRECTORY = 'zap-report'
        ZAP_RULES_FILE = 'zap-rules.conf'
        ZAP_CREDENTIAL_ID = 'accessflow-zap-test-user'
        ZAP_AUTH_HEADER_SITE = 'webimportexcel-dev.10.80.1.101.sslip.io'
        ZAP_TOKEN_FILE = 'zap-access-token.tmp'
        ZAP_SANITIZED_API_SPEC = 'zap-openapi-authorized.json'
    }

    stages {
        stage('Validate Configuration') {
            steps {
                script {
                    def target = params.TARGET_URL?.trim()
                    if (!target) {
                        error('TARGET_URL is required.')
                    }
                    if (!(target ==~ /^https?:\/\/.+/)) {
                        error('TARGET_URL must start with http:// or https://.')
                    }
                    def apiSpec = params.API_SPEC_URL?.trim()
                    if (!apiSpec) {
                        error('API_SPEC_URL is required.')
                    }
                    if (!(apiSpec ==~ /^https?:\/\/.+/)) {
                        error('API_SPEC_URL must start with http:// or https://.')
                    }
                    def loginUrl = params.AUTH_LOGIN_URL?.trim()
                    if (!loginUrl) {
                        error('AUTH_LOGIN_URL is required.')
                    }
                    if (!(loginUrl ==~ /^https?:\/\/.+/)) {
                        error('AUTH_LOGIN_URL must start with http:// or https://.')
                    }
                    if (!(params.SPIDER_MINUTES ==~ /^\d+$/) || params.SPIDER_MINUTES.toInteger() < 1) {
                        error('SPIDER_MINUTES must be a positive integer.')
                    }

                    env.ZAP_TARGET_URL = target
                    env.ZAP_API_SPEC_URL = apiSpec
                    env.ZAP_AUTH_LOGIN_URL = loginUrl
                    currentBuild.displayName = "#${env.BUILD_NUMBER} ${params.SCAN_MODE}"
                    currentBuild.description = "Web: ${target} | API: ${apiSpec}"
                }

                bat '''
                    @where docker
                    @docker version
                '''
            }
        }

        stage('Wait for Target') {
            steps {
                bat '''
                    @echo off
                    echo Waiting for %ZAP_TARGET_URL% ...

                    for /L %%I in (1,1,30) do (
                        curl.exe --fail --silent --show-error --max-time 10 "%ZAP_TARGET_URL%" > NUL 2>&1 && goto :target_ready
                        echo Attempt %%I/30: target is not ready; retrying in 10 seconds...
                        timeout /t 10 /nobreak > NUL
                    )

                    echo Target did not become ready within 5 minutes.
                    exit /b 1

                    :target_ready
                    echo Target is ready for OWASP ZAP.
                '''
            }
        }

        stage('Wait for Backend API') {
            steps {
                bat '''
                    @echo off
                    echo Waiting for OpenAPI specification at %ZAP_API_SPEC_URL% ...

                    for /L %%I in (1,1,30) do (
                        curl.exe --fail --silent --show-error --max-time 10 "%ZAP_API_SPEC_URL%" > NUL 2>&1 && goto :api_ready
                        echo Attempt %%I/30: API specification is not ready; retrying in 10 seconds...
                        timeout /t 10 /nobreak > NUL
                    )

                    echo Backend API specification did not become ready within 5 minutes.
                    exit /b 1

                    :api_ready
                    echo Backend API specification is ready for OWASP ZAP.
                '''
            }
        }

        stage('Prepare OWASP ZAP') {
            steps {
                bat '''
                    @echo off
                    if exist "%ZAP_REPORT_DIRECTORY%" rmdir /s /q "%ZAP_REPORT_DIRECTORY%"
                    mkdir "%ZAP_REPORT_DIRECTORY%"

                    docker image inspect "%ZAP_IMAGE%" > NUL 2>&1 || docker pull "%ZAP_IMAGE%"
                    if errorlevel 1 exit /b 1
                    docker build -t "%ZAP_WEB_IMAGE%" -f scripts/zap/Dockerfile scripts/zap
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Authenticate Backend API') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.ZAP_CREDENTIAL_ID,
                    usernameVariable: 'ZAP_TEST_USERNAME',
                    passwordVariable: 'ZAP_TEST_PASSWORD'
                )]) {
                    powershell '''
$ErrorActionPreference = 'Stop'

if (Test-Path -LiteralPath $env:ZAP_TOKEN_FILE) {
    Remove-Item -LiteralPath $env:ZAP_TOKEN_FILE -Force
}

$loginBody = @{
    Username = $env:ZAP_TEST_USERNAME
    Password = $env:ZAP_TEST_PASSWORD
    DeviceName = 'Jenkins OWASP ZAP DAST'
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri $env:ZAP_AUTH_LOGIN_URL `
        -Method Post `
        -ContentType 'application/json' `
        -Body $loginBody `
        -TimeoutSec 30
}
catch {
    throw "Backend authentication failed: $($_.Exception.Message)"
}

$accessToken = if ($response.accessToken) {
    [string]$response.accessToken
} elseif ($response.AccessToken) {
    [string]$response.AccessToken
} else {
    ''
}

if ([string]::IsNullOrWhiteSpace($accessToken)) {
    throw 'Backend login response did not contain accessToken or AccessToken.'
}

[System.IO.File]::WriteAllText(
    (Join-Path $env:WORKSPACE $env:ZAP_TOKEN_FILE),
    $accessToken,
    [System.Text.UTF8Encoding]::new($false)
)

$authorizationHeaders = @{ Authorization = "Bearer $accessToken" }
$loginUri = [Uri]$env:ZAP_AUTH_LOGIN_URL
$apiOrigin = $loginUri.GetLeftPart([UriPartial]::Authority)

try {
    Invoke-WebRequest `
        -Uri "$apiOrigin/api/auth/heartbeat" `
        -Method Post `
        -Headers $authorizationHeaders `
        -UseBasicParsing `
        -TimeoutSec 30 | Out-Null
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    throw "Access token preflight failed at /api/auth/heartbeat (HTTP $statusCode)."
}

try {
    $openApi = Invoke-RestMethod `
        -Uri $env:ZAP_API_SPEC_URL `
        -Method Get `
        -TimeoutSec 30
}
catch {
    throw "Unable to download OpenAPI specification: $($_.Exception.Message)"
}

# Active API scanning must not revoke the token that the scan itself is using.
$excludedPaths = @(
    '/api/auth/login',
    '/api/auth/refresh',
    '/api/auth/logout',
    '/api/auth/logout-all',
    '/api/auth/sessions/{sessionId}',
    '/api/auth/users/{userId}/sessions/{sessionId}',
    '/api/auth/users/{userId}/revoke'
)

foreach ($path in $excludedPaths) {
    if ($openApi.paths.PSObject.Properties.Name -contains $path) {
        $openApi.paths.PSObject.Properties.Remove($path)
    }
}

# A local OpenAPI file needs an explicit server so ZAP sends requests to DEV.
$openApi | Add-Member `
    -MemberType NoteProperty `
    -Name servers `
    -Value @(@{ url = $apiOrigin }) `
    -Force

$openApiJson = $openApi | ConvertTo-Json -Depth 100
[System.IO.File]::WriteAllText(
    (Join-Path $env:WORKSPACE $env:ZAP_SANITIZED_API_SPEC),
    $openApiJson,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host 'Backend authentication and heartbeat preflight succeeded.'
Write-Host 'A safe OpenAPI copy was created without login, logout, refresh, and session-revocation operations.'
'''
                }
            }
        }

        stage('OWASP ZAP Baseline Scan') {
            steps {
                script {
                    def scanOptions = params.SCAN_MODE == 'ENFORCE_RULES'
                        ? "-c /zap/wrk/${env.ZAP_RULES_FILE} -I"
                        : '-I'

                    if (params.SCAN_MODE == 'ENFORCE_RULES' && !fileExists(env.ZAP_RULES_FILE)) {
                        error("${env.ZAP_RULES_FILE} is required when SCAN_MODE=ENFORCE_RULES.")
                    }

                    withCredentials([usernamePassword(
                        credentialsId: env.ZAP_CREDENTIAL_ID,
                        usernameVariable: 'ZAP_TEST_USERNAME',
                        passwordVariable: 'ZAP_TEST_PASSWORD'
                    ), usernamePassword(
                        credentialsId: 'accessflow-zap-approver',
                        usernameVariable: 'ZAP_APPROVER_USERNAME',
                        passwordVariable: 'ZAP_APPROVER_PASSWORD'
                    ), usernamePassword(
                        credentialsId: 'accessflow-zap-user',
                        usernameVariable: 'ZAP_USER_USERNAME',
                        passwordVariable: 'ZAP_USER_PASSWORD'
                    )]) {
                    withEnv([
                        "ZAP_SCAN_OPTIONS=${scanOptions}",
                        "ZAP_SPIDER_MINUTES=${params.SPIDER_MINUTES}"
                    ]) {
                        bat '''
                            @echo off
                            docker run --rm ^
                                --shm-size=1g ^
                                -e ZAP_TEST_USERNAME ^
                                -e ZAP_TEST_PASSWORD ^
                                -e ZAP_APPROVER_USERNAME ^
                                -e ZAP_APPROVER_PASSWORD ^
                                -e ZAP_USER_USERNAME ^
                                -e ZAP_USER_PASSWORD ^
                                -v "%CD%:/zap/wrk/:rw" ^
                                "%ZAP_WEB_IMAGE%" ^
                                zap-baseline.py ^
                                -P 8090 ^
                                --hook=/zap/wrk/scripts/zap/permissions_hook.py ^
                                -t "%ZAP_TARGET_URL%" ^
                                -m "%ZAP_SPIDER_MINUTES%" ^
                                -j ^
                                %ZAP_SCAN_OPTIONS% ^
                                -r "%ZAP_REPORT_DIRECTORY%/zap-baseline.html" ^
                                -J "%ZAP_REPORT_DIRECTORY%/zap-baseline.json" ^
                                -w "%ZAP_REPORT_DIRECTORY%/zap-baseline.md"
                        '''
                    }
                    }
                    powershell '''
$coveragePath = Join-Path $env:WORKSPACE 'zap-report/permissions-coverage.json'
if (!(Test-Path -LiteralPath $coveragePath)) {
    throw 'Authenticated permissions coverage report is missing.'
}
$coverage = Get-Content -Raw -LiteralPath $coveragePath | ConvertFrom-Json
if ($coverage.passed -ne $true) {
    throw 'ZAP did not verify authenticated /permissions coverage. Check test-user role.manage permission and container DNS/browser access.'
}
'''
                }
            }
        }

        stage('OWASP ZAP API Scan') {
            steps {
                script {
                    def scanOptions = params.SCAN_MODE == 'ENFORCE_RULES'
                        ? "-c /zap/wrk/${env.ZAP_RULES_FILE} -I"
                        : '-I'

                    def accessToken = readFile(env.ZAP_TOKEN_FILE).trim()
                    if (!accessToken) {
                        error('Authorized API scan cannot start because the access token is empty.')
                    }

                    withEnv([
                        "ZAP_SCAN_OPTIONS=${scanOptions}",
                        'ZAP_AUTH_HEADER=Authorization',
                        "ZAP_AUTH_HEADER_VALUE=Bearer ${accessToken}"
                    ]) {
                        bat '''
                            @echo off
                            docker run --rm ^
                                -e ZAP_AUTH_HEADER ^
                                -e ZAP_AUTH_HEADER_VALUE ^
                                -e ZAP_AUTH_HEADER_SITE="%ZAP_AUTH_HEADER_SITE%" ^
                                -v "%CD%:/zap/wrk/:rw" ^
                                "%ZAP_IMAGE%" ^
                                zap-api-scan.py ^
                                -t "/zap/wrk/%ZAP_SANITIZED_API_SPEC%" ^
                                -f openapi ^
                                %ZAP_SCAN_OPTIONS% ^
                                -r "%ZAP_REPORT_DIRECTORY%/zap-api-authorized.html" ^
                                -J "%ZAP_REPORT_DIRECTORY%/zap-api-authorized.json" ^
                                -w "%ZAP_REPORT_DIRECTORY%/zap-api-authorized.md"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'zap-report/**',
                allowEmptyArchive: true,
                fingerprint: true
            )
            powershell '''
if (Test-Path -LiteralPath $env:ZAP_TOKEN_FILE) {
    Remove-Item -LiteralPath $env:ZAP_TOKEN_FILE -Force
}
if (Test-Path -LiteralPath $env:ZAP_SANITIZED_API_SPEC) {
    Remove-Item -LiteralPath $env:ZAP_SANITIZED_API_SPEC -Force
}
'''
        }
        success {
            echo "OWASP ZAP Web and API scans completed for ${env.ZAP_TARGET_URL} and ${env.ZAP_API_SPEC_URL}."
        }
        failure {
            echo "OWASP ZAP scan failed or the configured security gate rejected ${env.ZAP_TARGET_URL}."
        }
    }
}
