# Byte Pair Encoding Tokenizer

A small full-stack project for training and inspecting a Byte Pair Encoding tokenizer.

The app lets you select a text dataset, train a Basic or Regex BPE tokenizer, watch merges happen live, inspect vocabulary growth, and test encode/decode behavior from the UI.

## What Is BPE?

Byte Pair Encoding is a tokenization technique used in many language-model systems.

At the start, text is represented as raw bytes. The tokenizer then repeatedly finds the most common pair of neighboring tokens and merges that pair into a new token. Over time, frequent byte patterns become reusable tokens.

Simple idea:

```text
text -> bytes -> frequent pair merges -> vocabulary -> token ids
```

Example:

```text
"hello"
bytes: [104, 101, 108, 108, 111]
common pair: (104, 101) -> new token
encoded output becomes shorter over repeated merges
```

This project makes that process visible in the browser.

## Folder Structure

```text
bpe_tokenizer/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── tokenizer_modules/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── basic.py
│   │   │   └── regex_.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── schemas.py
│   ├── __init__.py
│   └── app_run.py
├── artifacts/
│   ├── law_of_human_nature.txt
│   └── rich_dad_poor_dad.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CompressionStats.jsx
│   │   │   ├── DatasetSelector.jsx
│   │   │   ├── EncodePanel.jsx
│   │   │   ├── TrainingPanel.jsx
│   │   │   └── VocabViewer.jsx
│   │   ├── api.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── tests/
│   ├── __init__.py
│   ├── test_base.py
│   ├── test_basic.py
│   └── test_regex.py
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Run With Docker

From the project root:

```powershell
docker compose up --build
```

If your machine uses Docker Compose v1:

```powershell
docker-compose up --build
```

Open:

```text
http://127.0.0.1:8001
```

Stop the container:

```powershell
docker compose down
```

or:

```powershell
docker-compose down
```

## Run Locally As One App

This is the simplest local development mode.

From the project root:

```powershell
uv run main.py
```

Open:

```text
http://127.0.0.1:8001
```

This does both:

```text
1. Builds the React frontend
2. Starts the FastAPI backend
```

The FastAPI app serves both:

```text
/api routes
React frontend
```

## Run Frontend And Backend Separately

Use this mode when actively editing the UI and you want Vite hot reload.

### Terminal 1: Backend

From the project root:

```powershell
uv run main.py
```

Backend runs on:

```text
http://127.0.0.1:8001
```

### Terminal 2: Frontend

From the project root:

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

In this mode, Vite proxies `/api` requests to the backend.

If you see this error:

```text
ECONNREFUSED /api/datasets
```

It means the frontend is running but the backend is not running on port `8001`.

## Backend-Only API Testing

For Postman/backend-only testing:

```powershell
cd app
uv run app_run.py
```

Then test:

```text
http://127.0.0.1:8001/api/health
http://127.0.0.1:8001/api/datasets
```

## Run Tests

From the project root:

```powershell
python -m pytest -v
```


## Common API Endpoints

```text
GET /api/health
```

Checks whether the API is running.

```text
GET /api/datasets
```

Lists available `.txt` datasets.

```text
GET /api/datasets/{filename}
```

Returns a preview of a dataset.

```text
POST /api/train/stream
```

Trains the tokenizer and streams live merge updates.

```text
POST /api/encode
```

Encodes text with the trained tokenizer.

```text
POST /api/decode
```

Decodes token ids back into text.

## Deployment Notes

This project has been prepared for deployment using:

```text
Azure Static Web Apps
Azure Container Apps
Docker Hub
GitHub Actions
```

Frontend production API URL is controlled by:

```text
VITE_API_URL
```

Local fallback:

```text
/api
```

See the deployment runbook for detailed cloud setup notes.