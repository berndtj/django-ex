pipeline {
    agent any
    environment {
        DEFAULT_AWS_REGION = 'us-west-2'
        REPO = '367199020685.dkr.ecr.us-west-2.amazonaws.com/photon/django-ex'
        DOCKER_API_VERSION = '1.23'
    }
    stages {
        stage('Test') {
            steps {
                echo 'Testing...'
                sh """
                    ./manage.py jenkins --enable-coverage
                """
                junit 'reports/*.xml'
            }
        }
        stage('Build') {
            steps {
                echo "Building ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                sh """
                    docker build -t ${env.REPO}:${env.BUILD_ID} .
                    sleep 5
                    push_ecs.sh ${env.REPO}:${env.BUILD_ID}
                """
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                sh """
                    helm_install.sh django-ex
                """
            }
        }
    }
}
