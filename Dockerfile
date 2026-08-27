# node:20-alpine - node.js version 20, small Alpine Linux image
FROM node:20-alpine AS frontend-builder       

# creating a folder inside the container
WORKDIR /frontend

# copies - frontend/package.json | package-lock.json inside the docker image
# done because docker can cache dependency installation, if there is change in source code but no chnage in 
# package.json docker does not reinstall all npm packages again. 
COPY frontend/package*.json ./

# install frontend dependencies, npm ci is better than npm install in docker because it uses package.json
RUN npm ci

# copying the rest of the frontend code into the image frontend/ src, index.html, vite.config.js
COPY frontend/ ./

# Builds the react frontend
RUN npm run build

# Starting the seconds docker stage, final container that will run the app
# python:3.12-slim - Python 3.12 small linux image
FROM python:3.12-slim AS runtime

# setting environment variable inside the container,
# PYTHONDONTWRITEBYTECODE=1,               : stops python from creating __pycache__ and .pyc 
# PYTHONUNBUFFERED=1                       : makes logs print immediately
# ARTIFACTS_DIR=/app/artifacts             : Tells the backend where the dataset .txt files are
# FRONTEND_DIST_DIR=/app/frontend/dist     : tells the backend where the build react frontend exists
# PORT=8001                                : App will run on port 8001
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARTIFACTS_DIR=/app/artifacts \
    FRONTEND_DIST_DIR=/app/frontend/dist \
    PORT=8001

# sets the backend working folder inside the container 
WORKDIR /app

# this installes the python dependencies
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
      fastapi \
      pydantic \
      regex \
      "uvicorn[standard]"

# copies the backend python package into the image
COPY app/ ./app/

# copy the dataset file into the docker image
COPY artifacts/ ./artifacts/

# copying the important root file into /app
COPY main.py pyproject.toml README.md ./

# Copy the built React app from the frontend build stage.
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# does not publish the port 8001, informs docker, actual port mapping happens in docker-compose.yml
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
