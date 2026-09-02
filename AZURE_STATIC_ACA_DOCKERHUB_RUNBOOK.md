# Azure Static Web Apps + Docker Hub + Azure Container Apps Runbook

## This branch has been developed to run on Azure Container Apps + Static web App

Important 
azure_static_aca_dockerhub - this branch is created for this the specific methodology 
- Docker Hub image repository + GitHub Actions automation Azure Container Apps[backend] + Azure Static Web Apps[frontend]

## 1. Final Architecture

```text
Developer pushes code to GitHub
        ↓
GitHub Actions builds Docker image
        ↓
Docker image is pushed to Docker Hub
        ↓
Azure Container Apps runs backend container
        ↓
Azure Static Web Apps hosts frontend
        ↓
Frontend calls backend through VITE_API_URL
```

---

## 3. Docker Hub Setup

Docker Hub repository created:

```text
aarizzafar/bpe_tokenizer_api
```

Docker Hub token name:

```text
bpe_tokenizer_github_actions
```

The token is used by GitHub Actions to push images automatically.

---

## 4. GitHub Secrets

Go to GitHub repo:

```text
Settings
→ Secrets and variables
→ Actions
→ Secrets
→ New repository secret
```

Add:

```text
DOCKERHUB_USERNAME     = aarizzafar
DOCKERHUB_TOKEN        = Docker Hub access token
VITE_API_URL           = https://cae-bpe-tokenizer-prod.lemonground-e369f4d7.eastus2.azurecontainerapps.io/api
```

Important:

```text
Secrets are encrypted.
Variables are plain config.
Tokens/passwords must be stored as Secrets, not Variables.
```

---

## 5. Docker Hub GitHub Action

Workflow file:

```text
.github/workflows/dockerhub-deploy.yml
```

Purpose:

```text
Whenever code is pushed to azure_static_aca_dockerhub,
GitHub Actions builds the Docker image and pushes it to Docker Hub.
```

Workflow:

```yaml
name: Build and push Docker Image

on:
  push:
    branches:
      - azure_static_aca_dockerhub

jobs:
  docker-build-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            aarizzafar/bpe_tokenizer_api:latest
            aarizzafar/bpe_tokenizer_api:${{ github.sha }}
```

After this runs successfully, Docker Hub shows tags:

```text
latest
<commit-sha>
```

## 8. Azure Container Apps Setup

Resource group used:

```text
rg_bpe_tokenizer_prod
```

Container App URL created:

```text
https://cae-bpe-tokenizer-prod.lemonground-e369f4d7.eastus2.azurecontainerapps.io
```

Container App image:

```text
aarizzafar/bpe_tokenizer_api:latest
```

Container settings:

```text
Command override:   empty
Arguments override: empty
```

Reason:

```text
The Dockerfile already contains the startup CMD.
Azure Container Apps should use that command.
```

Environment variables:

```text
ARTIFACTS_DIR       = /app/artifacts
FRONTEND_DIST_DIR   = /app/frontend/dist
PORT=8001
```

Ingress settings:

```text
Ingress: Enabled
Accept traffic from anywhere: Yes
Target port: 8001
Transport: Auto
```

Test backend:

```text
https://cae-bpe-tokenizer-prod.lemonground-e369f4d7.eastus2.azurecontainerapps.io/api/health
```

Expected:

```json
{"status":"ok","tokenizer_trained":false,"tokenizer_type":null}
```

Test datasets:

```text
https://cae-bpe-tokenizer-prod.lemonground-e369f4d7.eastus2.azurecontainerapps.io/api/datasets
```

Expected:

```json
{
  "datasets": [
    "law_of_human_nature.txt",
    "rich_dad_poor_dad.txt"
  ]
}
```

---

## 9. Why Container App Shows Full UI

The Container App URL shows the full UI at `/` because the Docker image includes the built React frontend.

This is expected because FastAPI serves:

```text
/api/* = backend APIs
/      = React frontend
```

For the final architecture, we use the Container App mainly as backend:

```text
https://container-app-url/api
```

The public UI is hosted separately by Azure Static Web Apps.

---

## 10. Azure Static Web Apps Setup

Static Web App URL:

```text
https://lemon-dune-08f4e870f.7.azurestaticapps.net
```

Settings used:

```text
Resource group: rg_bpe_tokenizer_prod
Plan: Free / Hobby
Source: GitHub
Branch: azure_static_aca_dockerhub
App location: frontend
API location: empty
Output location: dist
```

Deployment authorization policy:

```text
GitHub
```

Reason:

```text
GitHub authorization lets Azure create/use GitHub Actions for automatic frontend deployments.
```

---

## 11. Static Web App Environment Variable

In Azure Static Web Apps portal:

```text
Environment           : Production
Name                  : VITE_API_URL
Value                 : https://cae-bpe-tokenizer-prod.lemonground-e369f4d7.eastus2.azurecontainerapps.io/api
```

Important:

```text
Vite reads VITE_API_URL at build time.
If this is changed after deployment, the Static Web App must be rebuilt/redeployed.
```

## 14. Static Web Apps Workflow Fix

Azure created this workflow:

```text
.github/workflows/azure-static-web-apps-lemon-dune-08f4e870f.yml
```

We added `VITE_API_URL` to the build/deploy step:

```yaml
- name: Build And Deploy
  id: builddeploy
  uses: Azure/static-web-apps-deploy@v1
  env:
    VITE_API_URL: ${{ secrets.VITE_API_URL }}
  with:
    azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN_LEMON_DUNE_08F4E870F }}
    action: upload
    app_location: ./frontend
    api_location: ""
    output_location: dist
    github_id_token: ${{ steps.idtoken.outputs.result }}
```

Important:

```text
The VITE_API_URL secret must exist in GitHub Actions secrets.
```

Need to rebased with the git hub code because local code is 1 commit back

---
