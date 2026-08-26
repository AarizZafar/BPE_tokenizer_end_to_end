pipeline {
  agent any

  environment {
    APP_NAME = 'bpe-tokenizer'
    IMAGE_NAME = 'bpe-tokenizer'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    DOCKER_BUILDKIT = '1'
  }

  options {
    timestamps()
    skipDefaultCheckout(false)
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Python Setup') {
      steps {
        bat '''
          python --version
          python -m pip install --upgrade pip
          python -m pip install fastapi pydantic regex "uvicorn[standard]" httpx pytest pytest-asyncio
        '''
      }
    }

    stage('Backend Tests') {
      steps {
        bat '''
          python -m pytest
        '''
      }
    }

    stage('Frontend Build') {
      steps {
        dir('frontend') {
          bat '''
            npm ci
            npm run build
          '''
        }
      }
    }

    stage('Docker Compose Validate') {
      steps {
        bat '''
          docker compose config
        '''
      }
    }

    stage('Docker Build') {
      steps {
        bat '''
          docker build -t %IMAGE_NAME%:%IMAGE_TAG% -t %IMAGE_NAME%:latest .
        '''
      }
    }
  }

  post {
    success {
      echo "Pipeline completed successfully. Built image: ${IMAGE_NAME}:${IMAGE_TAG}"
    }

    failure {
      echo 'Pipeline failed. Check the stage logs above.'
    }
  }
}
