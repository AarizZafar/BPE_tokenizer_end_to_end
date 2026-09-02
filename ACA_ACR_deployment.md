# Azure Container Apps Deployment Guide

This document records the full deployment flow used for the BPE Tokenizer project so you can repeat it later or understand each step again.

## Final Architecture

```text
React + FastAPI app
        ↓
Docker image
        ↓
Azure Container Registry
        ↓
Azure Container App
        ↓
Public URL on port 8001
```

## 1. Create Resource Group

In Azure Portal:

```text
Search: Resource groups
→ Create
```

Use:

```text
Resource group   : bpe-tokenizer-rg
Region           : East US
```

Then click:

```text
Review + create
→ Create
```

Why this is needed:

```text
A resource group keeps all related Azure resources together:
Container Registry, Container App, networking, logs, etc.
```

---

## 2. Create Azure Container Registry

In Azure Portal:

```text
Search: Container registries
→ Create
```

Use:

```text
Registry name      : bpetokenizeracr
Resource group     : bpe-tokenizer-rg
Location           : East US
SKU                : Basic
```

Then click:

```text
Review + create
→ Create
```

Why this is needed:

```text
Azure Container Registry stores your Docker image.
Azure Container Apps pulls the image from this registry.
```

---

## 3. Enable Registry Admin User

After the registry is created:

```text
Container Registry
→ bpetokenizeracr
→ Access keys
```

Turn on:

```text
Admin user: Enabled
```

Copy:

```text
Login server
Username
Password
```

Example login server:

```text
bpetokenizeracr.azurecr.io
```

Why this is needed:

```text
Docker needs credentials to push the image into Azure Container Registry.
```

---

## 4. Login To Azure Container Registry From PowerShell

Open PowerShell and run:

```powershell
docker login bpetokenizeracr.azurecr.io
```

Use the username/password from:

```text
Azure Container Registry → Access keys
```

Expected result:

```text
Login Succeeded
```

If you get Docker engine error:

```text
failed to connect to the docker API
```

Then start Docker Desktop first and verify:

```powershell
docker ps
```

## 6. Build Docker Image

Run:

```powershell
docker build -t bpetokenizeracr.azurecr.io/bpe-tokenizer-api:latest .
```

What this does:

```text
Builds the Docker image from Dockerfile.
Tags it with the Azure Container Registry address.
```

Meaning of the tag:

```text
bpetokenizeracr.azurecr.io/bpe-tokenizer-api:latest
```

Breakdown:

```text
bpetokenizeracr.azurecr.io  = Azure Container Registry login server
bpe-tokenizer-api           = image name
latest                      = image tag/version
```

---

## 7. Push Docker Image To Azure Container Registry

Run:

```powershell
docker push bpetokenizeracr.azurecr.io/bpe-tokenizer-api:latest
```

Expected result includes something like:

```text
latest: digest: sha256:...
```

That means the image was pushed successfully.

---

## 8. Create Azure Container App

In Azure Portal:

```text
Search: Container Apps
→ Create
```

### Basics Tab

Use:

```text
Subscription: your subscription
Resource group: bpe-tokenizer-rg
Container app name: bpe-tokenizer-api
Region: East US
```

For Container Apps Environment:

```text
Create new
Name: bpe-tokenizer-env
```

Then click:

```text
Next: Container
```

---

## 9. Configure Container Image

On the Container tab:

```text
Image source: Azure Container Registry
Registry: bpetokenizeracr
Image: bpe-tokenizer-api
Tag: latest
```

Resources:

```text
CPU: 0.5
Memory: 1Gi
```

Environment variables:

```text
ARTIFACTS_DIR=/app/artifacts
FRONTEND_DIST_DIR=/app/frontend/dist
PORT=8001
```

Why these are needed:

```text
ARTIFACTS_DIR tells FastAPI where dataset files are.
FRONTEND_DIST_DIR tells FastAPI where the React build is.
PORT documents the app port.
```

Then click:

```text
Next: Ingress
```

---

## 10. Configure Ingress

Use:

```text
Ingress: Enabled
Accepting traffic from anywhere: Yes
Ingress type: HTTP
Transport: Auto
Target port: 8001
```

Why target port is 8001:

```text
Your Dockerfile starts Uvicorn on port 8001.
Azure Container Apps must forward traffic to the same container port.
```

Then click:

```text
Review + create
→ Create
```

---

## 11. Get Application URL

After deployment completes:

```text
Container Apps
→ bpe-tokenizer-api
→ Overview
```

Copy:

```text
Application URL
```

It will look like:

```text
https://bpe-tokenizer-api.xxxxx.eastus.azurecontainerapps.io
```

---

## 12. Test Backend Health

Open in browser:

```text
https://YOUR_CONTAINER_APP_URL/api/health
```

Expected response:

```json
{
  "status": "ok",
  "tokenizer_trained": false,
  "tokenizer_type": null
}
```

---

## 13. Test Dataset Endpoint

Open:

```text
https://YOUR_CONTAINER_APP_URL/api/datasets
```

Expected response:

```json
{
  "datasets": [
    "law_of_human_nature.txt",
    "rich_dad_poor_dad.txt"
  ]
}
```

If this returns:

```json
{"datasets": []}
```

Then check that the Docker image contains the artifacts folder and that `docker-compose.yml` is not mounting an empty artifacts folder over it.

Your Dockerfile should include:

```dockerfile
COPY artifacts/ ./artifacts/
```

---

## 14. Dockerfile Used

Important lines:

```dockerfile
COPY artifacts/ ./artifacts/
COPY --from=frontend-builder /frontend/dist ./frontend/dist
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Meaning:

```text
Artifacts are copied into the image.
React build is copied into the image.
Uvicorn starts FastAPI on port 8001.
```
