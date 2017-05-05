pipeline {
    agent any

    def repo = '367199020685.dkr.ecr.us-west-2.amazonaws.com/photon/django-ex'

    stages {
        stage('Build') {
            steps {
                kubectl get pods
                echo 'Building ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                docker build -t '${repo}:${env.BUILD_ID}' .
                docker push '${repo}:${env.BUILD_ID}'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
