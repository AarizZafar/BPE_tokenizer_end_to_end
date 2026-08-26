FROM node:20-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/src ./backend/src
COPY backend/main.py ./backend/main.py
COPY artifacts/ /artifacts/
COPY --from=frontend-builder /frontend/dist ./frontend/dist

ENV ARTIFACTS_DIR=/artifacts
ENV FRONTEND_DIST_DIR=/app/frontend/dist
ENV PYTHONPATH=/app/backend/src
ENV PORT=8001
EXPOSE 8001

CMD ["uvicorn", "bpe_tokenizer.app:app", "--host", "0.0.0.0", "--port", "8001"]
