# AccessFlow RBAC Portal

Nuxt 3 web portal for the Oracle RBAC + JWT API in `WebImportExcel`.

Requires Node.js 24 LTS. The production baseline is pinned to Node.js 24.19.0.

## Run locally

1. Verify the Node.js version. It must be `v24.19.0` or a newer v24 release:

```powershell
node --version
```

2. Start `WebImportExcel` at `http://localhost:5109`.
3. Optionally start Redis. If `NUXT_REDIS_URL` is not set, local development uses an in-memory session store and all sessions are lost when Nuxt restarts:

```powershell
docker run --name accessflow-redis -p 6379:6379 -d redis:7.4-alpine redis-server --appendonly yes --requirepass "your-development-password"
$env:NUXT_REDIS_URL = "redis://localhost:6379"
$env:NUXT_REDIS_PASSWORD = "your-development-password"
```

4. Install and start the portal:

```powershell
cd web-portal
npm install
npm run dev
```

5. Open `http://localhost:3000`.

The Nuxt server is a Backend-for-Frontend (BFF). It stores access and refresh tokens in Redis (or memory for local development), gives the browser only an opaque `HttpOnly` session cookie, and adds the Bearer token while forwarding `/backend/**` to the .NET API. Browser CORS configuration is not required locally.

While development is HTTP-only, `NUXT_SESSION_COOKIE_SECURE` is `false`. Set it to `true` as soon as HTTPS is enabled. The cookie remains `HttpOnly` and `SameSite=Lax` in both modes.

## Jenkins, Docker, Kind and Helm deployment

Create a separate Jenkins Pipeline job and configure:

- Repository: the same repository as the API
- Script Path: `Jenkinsfile.web`
- Jenkins agent: the Windows machine running Docker Desktop
- Required tools: Node.js 24 LTS, Docker Desktop, Kind, kubectl, Helm, OSV-Scanner and Trivy
- Jenkins integrations: `SonarQube-Local` and HashiCorp Vault AppRole credential `vault-jenkins-approle`

The pipeline requires a Git tag in the existing format:

```text
v1.0.0-dev
v1.0.0-uat
v1.0.0-prod
```

The quality and security gates run in this order:

```text
Git tag → npm ci → OSV → Unit Test/Coverage → Type Check
→ SonarQube/Quality Gate → Docker Build → Trivy
→ Kind Load → Vault Secret → Helm Lint/Package/Deploy → Rollout Check
```

Add this Vault key to the existing WebImport secret for each environment:

```text
Path: secret/jenkins/webimport/dev
Key:  NUXT_API_PROXY_TARGET
Value: http://webimportexcel-service:80

Key:  REDIS_PASSWORD
Value: <a long, randomly generated password>
```

Repeat for `uat` and `prod`. The API and frontend are expected to run in the same Kubernetes namespace. Docker Desktop and the Kind cluster named `demo` must be running before the pipeline starts.

The Helm hosts are:

```text
dev:  dev.accessflow.local
uat:  uat.accessflow.local
prod: accessflow.local
```

Manual verification:

```powershell
kubectl get pods,service,ingress -n dev -l app=accessflow-web
helm status accessflow-web -n dev
```

## Dependency security updates (2026-10-06)

The OSV findings from Jenkins build 100 are addressed in `package-lock.json`:
Vue/server-renderer 3.5.43, seroval 1.6.3, source-map-js 1.2.2,
postcss-selector-parser 7.1.6, simple-git 4.0.2 and its argv-parser 2.0.1.
Vue's declared minimum is now 3.5.42; targeted overrides keep the transitive fixes.

Nuxt DevTools 3.4.2 still imports the removed simple-git default export. The tracked
`patches/@nuxt+devtools+3.4.2.patch` switches that import to the supported named
`simpleGit` export. `postinstall` runs `patch-package --error-on-fail`, so an
incompatible patch stops installation instead of silently leaving broken tooling.
The Docker dependency stage copies `patches/` before `npm ci` for the same behaviour.
Keep DevTools pinned until an upstream release supports simple-git v4; when upgrading,
review and remove the compatibility patch and pin together if no longer necessary.

No vulnerability exclusions were added. The two existing time-limited exceptions in
`osv-scanner.toml` remain; a passing configured scan is not an unfiltered clean bill.

## Authentication storage

- The browser must not contain `accessToken` or `refreshToken` in Local Storage.
- The legacy `accessflow.session` Local Storage entry is removed automatically.
- The browser receives only the `accessflow.sid` HttpOnly cookie.
- Kubernetes deploys an internal Redis service named `accessflow-web-redis` for BFF sessions.
- Redis uses password authentication and persistent AOF storage backed by a PVC.
- The `dev` environment exposes Redis as NodePort `30379`. On Docker Desktop, use a localhost-only Docker TCP proxy when the node network is not directly reachable from Windows.
- UAT and production keep Redis internal as a `ClusterIP` service.

Before using more than one frontend replica in a real UAT/production cluster, replace the bundled development Redis with a managed or highly available Redis service and restrict access with network policy and authentication.

## Implemented API integration

- Server-side login, refresh token rotation and logout through the Nuxt BFF
- Automatic server-side refresh and one retry after access-token expiration
- List and revoke sessions
- Permission-protected Abatement API tests
- Navigation and action visibility driven by permissions returned from login

The Role/Permission and User screens are currently UI prototypes because the .NET project does not yet expose administration CRUD endpoints for these tables.
