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

This is a given.  We are using a standard kubernetes, installed via <a href="https://kubernetes.io/docs/getting-started-guides/kops/">Kops</a>.

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

- <a href="https://jenkins.io/doc/book/pipeline/jenkinsfile/">Jenkinsfile</a> to define the CI/CD pipeline
- <a href="https://github.com/kubernetes/helm/blob/master/docs/charts.md">Helm Charts</a> to define the kubernetes deployment
- <a href="https://docs.docker.com/engine/reference/builder/#environment-replacement">Dockerfile</a> to define the application image

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

The pipeline has 4 stages: build, test, publish and deploy.  The build stage
simply uses the included Dockerfile to build the application image.

The test stage runs unit-tests via the built image.  Because there are no
application specific packages on the Jenkins Agent image, all application
specific processes (i.e. unit-tests) should be run via docker.

The publish stage simply pushes the image to the AWS ECR registry.

The deploy stage deploys the application onto the kubernetes cluster.  If
the application is already deployed, a rolling upgrade will be performed.
This is all orchestrated via the Helm Chart.

## Demo steps:
1. Make sure you have a user on a lightwave installation (you will need this
   to login to Jenkins)
1. Add the photon charts repo:
    1. helm repo add photon	https://berndtj.github.io/charts/photon
    1. helm repo update
1. Set the name for your jenkins cluster: `JENKINS_NAME=demo`
1. Deploy the chart: 
    ```
    export LIGHTWAVE_HOST='<lightwave host>' # e.g. lightwave01.kops.bjung.net
    export LIGHTWAVE_ROOT_DN='<lightwave root DN>' # e.g. dc=kops\,dc=bjung\,dc=net
    export LIGHTWAVE_PASSWORD='<lightwave manager password>'
    helm install --debug --name $JENKINS_NAME \
        --set Security.Lightwave.Server="$LIGHTWAVE_HOST" \
        --set Security.Lightwave.RootDN="$LIGHTWAVE_ROOT_DN" \
        --set Security.Lightwave.ManagerPassword="$LIGHTWAVE_PASSWORD" \
        photon/jenkins
    ```
1. Wait for a few minutes for the cluster to deploy...
1. `SERVICE_ENDPOINT=$(kubectl get svc $JENKINS_NAME-jenkins --namespace default --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")`
1. `printf "url: http://$SERVICE_ENDPOINT:8080/blue\n"`
1. Use the lightwave credentials and url to login to Jenkins
1. Fork `https://github.com/berndtj/django-ex` into your own organization
1. Create new pipeline and point to the new repo
1. Add a webhook to the repository
    - Open `echo "http://$SERVICE_ENDPOINT:8080/user/admin/configure"`
        - Get the API token (`Show API Token...`)
        - `API_TOKEN=<admin API token>`
    - From the github repository -> setting -> webhooks -> add webhook
    - `GITHUB_ORG=<your org>` (e.g. berndtj or your github username)
    - `echo "http://admin:$API_TOKEN@$SERVICE_ENDPOINT:8080/job/$GITHUB_ORG/job/django-ex/job/master/build"`
1. Kick back and relax!
