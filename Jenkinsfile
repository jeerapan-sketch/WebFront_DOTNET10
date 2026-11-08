pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        BUILD_CONFIGURATION = 'Release'
        IMAGE_NAME = 'webimportexcel'
        IMAGE_PLATFORM = 'linux/amd64'
        REGISTRY_HOST = '10.80.1.220:5050'
        REGISTRY_PROJECT = 'sarun/webimportexcel'
        REGISTRY_CREDENTIAL_ID = 'token-user-sarun'
        GITOPS_REPOSITORY_SSH = 'ssh://git@ssh.github.com:443/jeerapan-sketch/WebAPI_DOTNET10.git'
        GITOPS_CREDENTIAL_ID = 'github-gitops-ssh'
        GITOPS_BRANCH = 'dev'
        GITOPS_VALUES_FILE = 'helm/argoCD/webimportexcel/values.yaml'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate Registry Configuration') {
            steps {
                script {
                    if (!env.REGISTRY_HOST?.trim()) {
                        error('REGISTRY_HOST is required, for example 10.80.1.220:5050')
                    }
                    if (!env.REGISTRY_PROJECT?.trim()) {
                        error('REGISTRY_PROJECT is required, for example sarun/webimportexcel')
                    }
                    if (!env.REGISTRY_CREDENTIAL_ID?.trim()) {
                        error('REGISTRY_CREDENTIAL_ID is required')
                    }
                    if (!env.GITOPS_REPOSITORY_SSH?.trim()) {
                        error('GITOPS_REPOSITORY_SSH is required')
                    }
                    if (!env.GITOPS_CREDENTIAL_ID?.trim()) {
                        error('GITOPS_CREDENTIAL_ID is required')
                    }
                }

                bat '''
                    @where docker
                    @docker version
                '''
            }
        }

        stage('Fetch Tags') {
            steps {
                bat 'git fetch --tags'
            }
        }

        stage('Check Tag') {
            steps {
                script {

                    def tag = bat(
                        script: 'git describe --tags --exact-match',
                        returnStatus: true
                    )

                    if(tag != 0){
                        currentBuild.result = 'NOT_BUILT'
                        error("Current Commit is not tagged.")
                    }

                    def tagName = bat(
                        script: '@git describe --tags --exact-match',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_TAG = tagName.toString()

                    echo "Tag = '${tagName}'"
                    echo "env.IMAGE_TAG = '${env.IMAGE_TAG}'"

                    if (!("${tagName}" ==~ /^v\d+\.\d+\.\d+-(dev|uat|prod)$/)) {
                        error("Invalid tag format: ${tagName}. Expected v<major>.<minor>.<patch>-<dev|uat|prod>, for example v1.0.11-dev")
                    }

                    env.IMAGE_TAG = tagName.toString()
                    env.REGISTRY_IMAGE = "${env.REGISTRY_HOST}/${env.REGISTRY_PROJECT}"

                    echo "Tag = ${env.IMAGE_TAG}"
                    echo "Registry image = ${env.REGISTRY_IMAGE}:${env.IMAGE_TAG}"
                }
            }
        }

        stage('Restore') {
            steps {
                bat 'dotnet restore WebAPI_DOTNET10.slnx --locked-mode'
            }
        }

        stage('OSV Dependency Scan') {
            steps {
                bat '''
                    set "OSV_SCANNER=C:\\Tools\\osv-scanner\\osv-scanner.exe"

                    "%OSV_SCANNER%" --version

                    "%OSV_SCANNER%" scan source -r ^
                    WebImportExcel WebImportExcel.Test ^
                    --format json ^
                    --output-file osv-report.json

                    set "OSV_EXIT=%ERRORLEVEL%"

                    if exist "osv-report.json" type osv-report.json

                    if %OSV_EXIT% EQU 1 (
                        echo OSV-Scanner found vulnerable dependencies.
                        exit /b 1
                    )

                    if NOT %OSV_EXIT% EQU 0 (
                        echo OSV-Scanner failed with exit code %OSV_EXIT%.
                        exit /b %OSV_EXIT%
                    )
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'osv-report.json', allowEmptyArchive: true
                }
            }
        }

        stage('Build') {
            steps {
                bat 'dotnet build -c Release'
            }
        }

        stage('Unit Test') {
            steps {
                   bat 'dotnet test --configuration Release --no-build'
            }
        }

        stage('Build, Test and SonarQube Scan') {
            steps {
                withSonarQubeEnv('SonarQube-Local') {
                    bat '''
                        if not exist ".sonar-tools\\dotnet-sonarscanner.exe" (
                            dotnet tool install --tool-path .sonar-tools dotnet-sonarscanner
                            if errorlevel 1 exit /b 1
                        )

                        if not exist ".coverage-tools\\dotnet-coverage.exe" (
                            dotnet tool install --tool-path .coverage-tools dotnet-coverage
                            if errorlevel 1 exit /b 1
                        )

                        if exist ".sonarqube" rmdir /s /q ".sonarqube"
                        if exist "coverage.xml" del /q "coverage.xml"

                        .sonar-tools\\dotnet-sonarscanner begin ^
                        /k:"WebImportExcel" ^
                        /n:"WebImportExcel" ^
                        /v:"%IMAGE_TAG%" ^
                        /d:sonar.host.url="%SONAR_HOST_URL%" ^
                        /d:sonar.token="%SONAR_AUTH_TOKEN%" ^
                        /d:sonar.cs.vscoveragexml.reportsPaths="coverage.xml" ^
                        /d:sonar.exclusions="tmp/**,.codex-spreadsheet-work/**,publish/**,**/bin/**,**/obj/**,web-portal/**,helm/accessflow-web/**,Jenkinsfile.web,trivy-report.html,**/trivy-report.html" ^
                        /d:sonar.coverage.exclusions="scripts/**,**/DataAccess/**,**/Authentication/OracleAuthRepository.cs,**/Services/Abatement.cs,**/Services/BaseLog.cs,**/Program.cs,**/Model/**"
                        if errorlevel 1 exit /b 1

                        if not exist ".sonarqube\\conf\\SonarQubeAnalysisConfig.xml" (
                            echo SonarScanner begin did not create the analysis configuration
                            exit /b 1
                        )

                        dotnet build WebAPI_DOTNET10.slnx --no-incremental
                        if errorlevel 1 exit /b 1

                        powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Test-FifoCoverage.ps1
                        if errorlevel 1 exit /b 1

                        if not exist "coverage.xml" (
                            echo Coverage report was not created
                            exit /b 1
                        )

                        .sonar-tools\\dotnet-sonarscanner end ^
                        /d:sonar.token="%SONAR_AUTH_TOKEN%"
                        if errorlevel 1 exit /b 1
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Publish') {
            steps {
                bat 'dotnet publish WebImportExcel/WebImportExcel.csproj -c Release -o publish'
            }
        }

        stage('Docker Build') {
            steps {
                // Pull patched .NET base images and avoid reusing vulnerable runtime layers.
                // Publish a single-platform image for the current registry. Provenance
                // attestations create an index that this registry failed to accept (#175).
                bat "docker build --pull --no-cache --platform ${env.IMAGE_PLATFORM} --provenance=false -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."
            }
        }


        stage('Verify .NET Runtime') {
            steps {
                // Record the runtime version contained in the image before Trivy scans it.
                bat "docker run --rm --entrypoint dotnet ${env.IMAGE_NAME}:${env.IMAGE_TAG} --list-runtimes"
            }
        }

        stage('Trivy Scan') {
            steps {
                bat """
                C:\\Tools\\trivy\\trivy.exe image ^
                --severity HIGH,CRITICAL ^
                --exit-code 1 ^
                ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                """
            }
        }


       stage('Publish Report Trivy') {
            steps {
                bat """
                    C:\\Tools\\trivy\\trivy.exe image ^
                    --severity HIGH,CRITICAL ^
                    --format table ^
                    --output trivy-report.txt ^
                    ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                """

                powershell '''
$content = Get-Content -Path "trivy-report.txt" -Raw
$encoded = [System.Net.WebUtility]::HtmlEncode($content)

$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Trivy Security Report</title>
</head>
<body>
  <h1>Trivy Security Report</h1>
  <pre>$encoded</pre>
</body>
</html>
"@

$html | Out-File -FilePath "trivy-report.html" -Encoding utf8
'''
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat "docker images"
            }
        }

        stage('Login Registry') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.REGISTRY_CREDENTIAL_ID,
                    usernameVariable: 'REGISTRY_USERNAME',
                    passwordVariable: 'REGISTRY_PASSWORD'
                )]) {
                    bat '''
                        @echo off
                        echo(%REGISTRY_PASSWORD%| docker login %REGISTRY_HOST% --username %REGISTRY_USERNAME% --password-stdin
                        if errorlevel 1 exit /b 1
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                powershell '''
$ErrorActionPreference = 'Stop'

try {
    docker tag `
        "$env:IMAGE_NAME`:$env:IMAGE_TAG" `
        "$env:REGISTRY_IMAGE`:$env:IMAGE_TAG"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    docker push --platform $env:IMAGE_PLATFORM "$env:REGISTRY_IMAGE`:$env:IMAGE_TAG"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    docker tag `
        "$env:REGISTRY_IMAGE`:$env:IMAGE_TAG" `
        "$env:REGISTRY_IMAGE`:latest"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    docker push --platform $env:IMAGE_PLATFORM "$env:REGISTRY_IMAGE`:latest"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    docker logout $env:REGISTRY_HOST
}
'''
            }
        }

        stage('Validate Helm Chart') {
            steps {
                bat 'helm lint helm/argoCD/webimportexcel'
            }
        }

        stage('Update GitOps Image') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: env.GITOPS_CREDENTIAL_ID,
                    keyFileVariable: 'GITOPS_SSH_KEY',
                    usernameVariable: 'GITOPS_SSH_USERNAME'
                )]) {
                    powershell '''
$ErrorActionPreference = 'Stop'

$env:GIT_SSH_COMMAND = "ssh -i `"$env:GITOPS_SSH_KEY`" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=accept-new"

git remote set-url origin $env:GITOPS_REPOSITORY_SSH
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git fetch origin $env:GITOPS_BRANCH
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git checkout -B gitops-image-update "origin/$env:GITOPS_BRANCH"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$valuesPath = $env:GITOPS_VALUES_FILE
$content = Get-Content -LiteralPath $valuesPath -Raw
$content = $content -replace '(?m)^(\\s*repository:\\s*).+$', "`${1}$env:REGISTRY_IMAGE"
$content = $content -replace '(?m)^(\\s*tag:\\s*).+$', "`${1}$env:IMAGE_TAG"
[System.IO.File]::WriteAllText(
    (Resolve-Path -LiteralPath $valuesPath),
    $content,
    [System.Text.UTF8Encoding]::new($false)
)

git diff -- $valuesPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git add -- $valuesPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host 'GitOps image values already match the published image.'
    exit 0
}
if ($LASTEXITCODE -ne 1) { exit $LASTEXITCODE }

git config user.name 'Jenkins CI'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git config user.email 'jenkins-ci@localhost'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git commit -m "chore(gitops): deploy $env:IMAGE_TAG [skip ci]"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

git push origin "HEAD:$env:GITOPS_BRANCH"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
'''
                }
            }
        }

    }

    post {
        success {
            echo "Image published and GitOps manifest updated successfully"
        }

        failure {
            echo "CI/GitOps pipeline failed"
        }
    }
}
