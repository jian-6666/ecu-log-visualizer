pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.12'
        IMAGE_NAME = 'ecu-log-visualizer'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    pip install flake8
                    flake8 src/ --max-line-length=120 --exclude=__pycache__ || true
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running automated tests...'
                sh '''
                    pytest tests/ -v --cov=src --cov-report=term-missing --junitxml=test-results.xml
                '''
            }
        }
        
        stage('Build') {
            steps {
                echo "Building Docker image with tag ${BUILD_NUMBER}..."
                sh """
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
                """
            }
        }
    }
    
    post {
        always {
            echo 'Archiving test results...'
            junit 'test-results.xml'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}
