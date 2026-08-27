pipeline {
    agent any   // Run this pipeline on any available Jenkins agent/node

    // Environment variables used throughout the pipeline
    environment {
        REPO_URL = 'https://github.com/AarizZafar/BPE_tokenizer_end_to_end.git'
        BRANCH = 'main'
        SERVICE_NAME = 'bpe-tokenizer'
    }

    // Prevent Jenkins from automatically checking out the repository
    options {
        skipDefaultCheckout(true)
    }

    // Main list of pipeline stages
    stages {

        // Clone the GitHub repository
        stage('Clone') {
            steps {
                git branch: "${BRANCH}", url: "${REPO_URL}"
            }
        }

        stage('Run Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh 'python -m pip install --upgrade pip'
                    sh 'python -m pip install fastapi pydantic regex "uvicorn[standard]" httpx pytest pytest-asyncio'
                    sh 'python -m pytest'
                }
            }
        }

        // Stop and remove containers/images from the previous deployment
        stage('Stop Old Containers') {
            steps {
                // "|| true" allows the pipeline to continue if no old containers exist
                sh 'docker-compose down --rmi local || true'
            }
        }

        // Build the Docker image and start the container in detached mode
        stage('Build And Run') {
            steps {
                sh 'docker-compose up --build -d'
            }
        }

        // Verify that the application/container started correctly
        stage('Health Check') {
            steps {

                // Give the application some time to start
                sleep(time: 15, unit: 'SECONDS')

                // Display the status of Docker Compose services
                sh 'docker-compose ps'

                // Check the API health endpoint from inside the container
                sh '''
                    docker-compose exec -T ${SERVICE_NAME} python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/api/health').read().decode())"
                '''
            }
        }
    }

    // Actions executed after the pipeline finishes
    post {

        // Runs only if all stages succeed
        success {
            echo 'Deployment successful'
        }
        
        unstable {
            echo 'Deployment successful, but tests failed.'
        }

        // Runs if any stage fails
        failure {
            echo 'Deployment failed'

            // Print container logs to help debug the failure
            sh 'docker-compose logs ${SERVICE_NAME} || true'
        }
    }
}