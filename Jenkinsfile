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
                retry(3) {
                    sh """
                        sleep 5
                        push_ecs.sh ${env.REPO}:${env.BUILD_ID}
                    """
                }
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                sh """
                    ls /usr/local/bin
                    helm init
                    helm package --version 0.1.0-build.${env.BUILD_ID} helm/django-ex
                    helm upgrade ${env.JOB_NAME} django-ex-0.1.0-build.${env.BUILD_ID}.tgz --set image.repository=${env.REPO} --set image.tag=${env.BUILD_ID}
                """
                echo 'Deploying....'
            }
        }
    }
}
