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
                echo 'Deploying....'
                sh """
                    helm init
                    helm package --version 0.1.0-build.${env.BUILD_ID} helm/django-ex
                    RELEASE=$(helm list -q | grep ${env.JOB_NAME} | sort | head -n1)
                    if [[ $RELEASE == ${env.JOB_NAME} ]]; then
                        helm upgrade ${env.JOB_NAME} django-ex-0.1.0-build.${env.BUILD_ID}.tgz --install --reset-values --set image.repository=${env.REPO} --set image.tag=${env.BUILD_ID}
                    else
                        helm install django-ex-0.1.0-build.${env.BUILD_ID}.tgz --name ${env.JOB_NAME} --set image.repository=${env.REPO} --set image.tag=${env.BUILD_ID}
                    fi
                """
            }
        }
    }
}
