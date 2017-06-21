pipeline {
    agent any
    environment {
        REPO = ''
        IMAGE = 'library/django-ex'
        DOCKER_API_VERSION = '1.23'
    }
    stages {
        stage('Build') {
            steps {
                echo "Building ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                sh """
                    docker build -t ${env.REPO}/${env.IMAGE}:${env.BUILD_ID} .
                """
            }
        }
        stage('Test') {
            steps {
                echo 'Testing ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}..'
                // Run tests in built container, copy out artifacts (required)
                sh """
                    docker run -v /mnt/work/report:/report ${env.REPO}/${env.IMAGE}:${env.BUILD_ID} ./manage.py jenkins --enable-coverage --output-dir=/report
                    cp -r /work/report report
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
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'harborsecret',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh """
                        docker login -u $USERNAME -p $PASSWORD https://${env.REPO}
                        docker push ${env.REPO}/${env.IMAGE}:${env.BUILD_ID}
                    """
                }
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
                    helm_install.sh django-ex
                """
            }
        }
    }
}
