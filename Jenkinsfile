pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/AarizZafar/BPE_tokenizer_end_to_end.git'
        BRANCH = 'main'
        SERVICE_NAME = 'bpe-tokenizer'
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Clone') {
            steps {
                git branch: "${BRANCH}", url: "${REPO_URL}"
            }
        }

        stage('Stop Old Containers') {
            steps {
                sh 'docker-compose down --rmi local || true'
            }
        }

        stage('Build And Run') {
            steps {
                sh 'docker-compose up --build -d'
            }
        }

        stage('Health Check') {
            steps {
                sleep(time: 15, unit: 'SECONDS')
                sh 'docker-compose ps'
                sh '''
                    docker-compose exec -T ${SERVICE_NAME} python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/api/health').read().decode())"
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful'
        }

        failure {
            echo 'Deployment failed'
            sh 'docker-compose logs ${SERVICE_NAME} || true'
        }
    }
}