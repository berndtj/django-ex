pipeline {
    agent any
    environment {
        DEFAULT_AWS_REGION = 'us-west-2'
        REPO = '367199020685.dkr.ecr.us-west-2.amazonaws.com/photon/django-ex'
        DOCKER_API_VERSION = '1.23'
    }
    stages {
        stage('Build') {
            steps {
                echo "Building ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                sh """
                    docker build -t ${env.REPO}:${env.BUILD_ID} .
                """
            }
        }
        stage('Test') {
            steps {
                echo 'Testing ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                sh """
                    docker run -v /mnt/work/report:/report ${env.REPO}:${env.BUILD_ID} ./manage.py jenkins --enable-coverage --output-dir=/report
                    cp -r /work/report report
                """
                archiveArtifacts artifacts: 'report/*.xml'
                junit 'report/*.xml'
            }
        }
        stage('Publish') {
            steps {
                echo "Publishing ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                retry(3) {
                    sh """
                        sleep 5
                        push_ecs.sh ${env.REPO}:${env.BUILD_ID}
                    """
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                sh """
                    helm_install.sh django-ex
                """
            }
        }
    }
}
