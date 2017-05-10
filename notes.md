# Jenkins Pipelines on Kubernetes

Using helm charts and kubernetes creating an openshift style build/deploy
pipeline can be pretty simple.  This demo uses the following existing
technologies:

- kubernetes - deployed via Kops in AWS
- helm/charts - to deploy both jenkins and the demo application
- docker - to build and test
- AWS ECR - private container registry

## How it works

### Kubernetes

This is a given.  We are using a standard kubernetes, installed via Kops.

### Jenkins

We are deploying Jenkins with a select set of plugins via a helm chart.  The
chart has been modified slightly to allow for additional configuration.  The
deployed Jenkins will run a Jenkins master node, and spin up agents/slaves
on kubernetes, on demand.  Each build will get a fresh pod, thereby avoiding
many of the headaches associated with managing a Jenkins cluster.

The Jenkins Agent image is the container which runs the Jenkins jobs.  The idea
is to install only generic tools required to build and deploy a pipeline. The
Jenkins Agent image is extended from
[jenkinsci/jnlp-slave](https://hub.docker.com/r/jenkinsci/jnlp-slave/).  Our
Jenkins Agent image can be found at
[supervised-io/jenkins-agent](https://github.com/supervised-io/jenkins-agent).
Our Jenkins Agent image adds kubectl, docker, helm and the AWS cli to the image
as well as some helper scripts for use in the Jenkins pipeline file.

### The Demo App (django-ex)

This App is forked from a openshift demo, to give sort of an apples-to-apples
comparison.

Openshift uses a kubernetes style templates to define deployment as well as the
build.  Additionally they use "stem-cells" and a tool called "source-to-image"
to create the deployable application images.

Our solution is different.  We use standard, well understood formats:

- Jenkinsfile to define the CI/CD pipeline
- Helm Charts to define the kubernetes deployment
- Dockerfile to define the application image

At a minimum, the application directory structure should include the following:

```
.
├── Dockerfile
├── Jenkinsfile
├── README.md
├── helm
│   └── django-ex
│       ├── Chart.yaml
│       ├── templates
│       │   ├── NOTES.txt
│       │   ├── _helpers.tpl
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── values.yaml
```

#### Jenkinsfile

The Jenkinsfile defines the CI/CD pipline.  Below is the demo app's Jenkinsfile:

```
pipeline {
    agent any
    environment {
        DEFAULT_AWS_REGION = 'us-west-2'
        REPO = '367199020685.dkr.ecr.us-west-2.amazonaws.com/photon/django-ex'
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
                // Run tests in built container, copy out artifacts (required)
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
                sh """
                    push_ecs.sh ${env.REPO}:${env.BUILD_ID}
                """
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
```

The pipeline has 4 stages, build, test, publish and deploy.  The build stage
simply uses the included Dockerfile to build the application image.

The test stage runs unit-tests via the built image.  Because there are no
application specific packages on the Jenkins Agent image, all application
specific processes (i.e. unit-tests) should be run via docker.

The publish stage simply pushes the image to the AWS ECR registry.

The deploy stage deploys the application onto the kubernetes cluster.  If
the application is already deployed, a rolling upgrade will be performed.
This is all orchestrated via the Helm Chart.

## Demo steps:
1. `git clone https://github.com/berndtj/charts.git`
1. `cd charts`
1. `helm package stable/jenkins`
1. ```cat << EOF > jenkins.values.yaml
    Agent:
    Image: 367199020685.dkr.ecr.us-west-2.amazonaws.com/jenkins-agent
    ImageTag: latest
    Privileged: true
    MountDocker: true```
1. `JENKINS_NAME=demo`
1. `helm install jenkins-0.6.2.tgz --name $JENKINS_NAME -f jenkins.values.yaml`
1. `JENKINS_PASSWORD=$(kubectl get secret --namespace default $JENKINS_NAME-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode)`
1. Wait for a few minutes for the cluster to deploy...
1. `SERVICE_ENDPOINT=$(kubectl get svc $JENKINS_NAME-jenkins --namespace default --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")`
1. `printf "user: admin\npassword: $JENKINS_PASSWORD\nurl: http://$SERVICE_ENDPOINT:8080/blue\n"`
1. fork `https://github.com/berndtj/django-ex` into your own organization
1. create new pipeline and point to the new repo
    - `GITHUB_ORG=<your org>` (e.g. berndtj or your github username)
1. add a webhook to the repository
    - open `echo "http://$SERVICE_ENDPOINT:8080/user/admin/configure"`
        - get the API token (`Show API Token...`)
        - `API_TOKEN=<admin API token>`
    - from the github repository -> setting -> webhooks -> add webhook
    - `echo "http://admin:$API_TOKEN@$SERVICE_ENDPOINT:8080/job/$GITHUB_ORG/job/django-ex/job/master/build"`
1. kick back and relax!
