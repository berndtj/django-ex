pipeline {
    agent any
    environment {
        REPO = '367199020685.dkr.ecr.us-west-2.amazonaws.com/photon/django-ex'
    }
    stages {
        stage('Build') {
            steps {
                sh 'kubectl get pods'
                echo 'Building ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                sh 'docker build -t ${env.REPO}:${env.BUILD_ID} .'
                sh 'docker push ${env.REPO}:${env.BUILD_ID}'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
