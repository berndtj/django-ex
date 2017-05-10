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
                    docker build -t ${env.REPO}:${env.BUILD_ID} . | tee -a /tmp/result
                    printenv | tee -a /tmp/result
                """
            }
        }
        stage('Test') {
            steps {
                echo 'Testing ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                // Run tests in built container, copy out artifacts (required)
                sh """
                    docker run -v /mnt/work/report:/report ${env.REPO}:${env.BUILD_ID} ./manage.py jenkins --enable-coverage --output-dir=/report  | tee -a /tmp/result
                    cp -r /work/report report
                    push_logs.py /tmp/result --stream=${env.JOB_NAME}-${env.BUILD_ID}
                """
                archiveArtifacts artifacts: 'report/*.xml'
                junit 'report/*.xml'
            }
        }
        stage('Publish') {
            when {
                // Only publish master branch
                expression { env.JOB_BASE_NAME == 'master' }
            }
            steps {
                echo "Publishing ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                sh """
                    push_ecs.sh ${env.REPO}:${env.BUILD_ID} | tee -a /tmp/result
                """
            }
        }
        stage('Deploy') {
            when {
                // Only deploy master branch
                expression { env.JOB_BASE_NAME == 'master' }
            }
            steps {
                echo 'Deploying ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                sh """
                    helm_install.sh django-ex | tee -a /tmp/result
                """
            }
        }
    }
    post {
        always {
            script {
               sh """
                  push_logs.py /tmp/result --stream=${env.JOB_NAME}-${env.BUILD_ID}
               """
            }
        }
    }
}
