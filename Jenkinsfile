pipeline {
    agent any
    environment {
        // REPO is set as an agent env variable
        DEB_S3_BUCKET = 'kops-spinnaker-deb-repo'
        IMAGE = 'berndtj/example'
        DOCKER_API_VERSION = '1.23'
    }
    stages {
        stage('Build') {
            steps {
                echo "Building ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                sh """
                    docker build -t ${env.IMAGE}:${env.JOB_BASE_NAME}-${env.BUILD_ID} .
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
     	stage('Package') {
            steps {
                echo 'Building deb'
                sh """
                    dpkg-buildpackage -us -uc
                    cp ../*.deb .
                """
                archiveArtifacts artifacts: '*.deb'
                sh """
                    deb-s3 upload --endpoint s3-us-west-2.amazonaws.com --bucket ${env.DEB_S3_BUCKET} *.deb
                """
            }
        }
        stage('Publish') {
            steps {
                echo "Publishing ${env.JOB_NAME}:${env.BUILD_ID} on ${env.JENKINS_URL}.."
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'dockersecret',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh """
                        docker login -u $USERNAME -p $PASSWORD
                        docker push ${env.IMAGE}:${env.JOB_BASE_NAME}-${env.BUILD_ID}
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
                    DOMAIN_NAME=${env.DOMAIN_NAME}
                    if [ -z $DOMAIN_NAME ]; then
                        DOMAIN_NAME=photon
                    fi
                    helm upgrade --install django-ex-${env.JOB_BASE_NAME} \
                        --set=image.repoitory=${env.REPO} \
                        --set=image.tag=${env.BUILD_ID} \
                        --set=image.pullSecret=harborsecret \
                        --set=service.type=ClusterIP \
                        --set=ingress.enabled=true \
                        --set=ingress.hosts.0=django-ex.$DOMAIN_NAME \
                        helm/django-ex
                """
            }
        }
    }
}
