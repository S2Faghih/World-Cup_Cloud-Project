# GitLab Setup & CI/CD Pipeline Deployment

This guide provides a comprehensive, step-by-step walkthrough to set up a Minikube cluster, deploy GitLab, configure a GitLab Runner using Helm, and push your local repository to the cluster.
Prerequisites & Cluster Initialization

Start the Minikube cluster with sufficient resources (minimum 8 GB RAM and 4 CPUs) and create a dedicated Namespace for the project.

    Start Minikube with required resource allocation
    minikube start --memory=8192 --cpus=4

    Create the project namespace
    kubectl create namespace cc-project

## Step 1: Deploy GitLab

Apply the base deployment manifests to spin up the GitLab instance inside your cluster.

    kubectl apply -f gitlab-deployment.yaml -n cc-project

## Step 2: GitLab Authentication & Password Reset

To log in to the GitLab web UI, you must reset the default root user password using the Ruby on Rails console.

Note: Opening the interactive Rails console within the container may take a few minutes.


    kubectl exec -it deploy/gitlab -n cc-project -- gitlab-rails console

Once the Rails console is fully loaded, execute the following Ruby commands sequentially to change your password and exit:

    user = User.find_by_username('root')
    user.password = 'YOUR_NEW_PASSWORD'
    user.save!
    exit

## Step 3: Project and Runner Setup in GitLab Web UI

Retrieve your cluster’s IP address by running:

    minikube ip

    Open your web browser and navigate to: http://<Minikube-IP>:30880

Log in with the username root and the password you set in Step 2.

Create a new blank project named cloud-project (ensure you uncheck the option to initialize with a default README.md file).

From the left sidebar, go to Settings → CI/CD → Runners.

Click New project runner and name it k8s-runner.

Crucial Step: Copy the Authentication Token displayed on your screen immediately. It will only be shown once.

Open your local runner-values.yaml file and insert this token along with any other environment-specific configurations required.

## Step 4: Install GitLab Runner using Helm

Add the official GitLab Helm repository, update your local charts, and deploy the Runner into the cc-project namespace.

    Add and update the official repository
    helm repo add gitlab https://charts.gitlab.io
    helm repo update

    Install the GitLab Runner using your configuration values
    helm install gitlab-runner gitlab/gitlab-runner -n cc-project -f gitlab/runner-values.yaml

To prevent authorization or RBAC (Role-Based Access Control) errors during pipeline execution, grant cluster administrator permissions to the default ServiceAccount in your namespace:

    kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=cc-project:default -n cc-project

## Step 5: Push Local Code to the Local GitLab Repository

Link your local project directory to the newly configured remote GitLab instance in your cluster and push your branch:

    Add the remote repository
    git remote add gitlab http://<Minikube-IP>:30880/root/cloud-project.git

    Push the main branch to GitLab
    git push -u gitlab main

(Note: If your default local branch is named something other than main (e.g., master), replace main with your actual branch name.)

# 🛠 Troubleshooting: Offline/Cached Pipeline Images

If your CI/CD pipeline hangs on pulling base images (due to network latency, proxy configurations, or registry limits), you can pull the images to your local machine first and load them directly into Minikube’s internal registry.
## 1. Pull Images to Your Local Machine

    docker pull registry.docker.ir/library/python:3.9-slim

    docker pull registry.docker.ir/library/ubuntu:22.04

    docker pull gcr.io/kaniko-project/executor:debug

    docker pull registry.docker.ir/bitnami/kubectl:latest

    docker pull registry.docker.ir/gitlab/gitlab-runner-helper:x86_64-v16.11.2

## 2. Sideload Images into Minikube

    minikube image load registry.docker.ir/library/python:3.9-slim

    minikube image load registry.docker.ir/library/ubuntu:22.04

    minikube image load gcr.io/kaniko-project/executor:debug

    minikube image load registry.docker.ir/bitnami/kubectl:latest

    minikube image load registry.docker.ir/gitlab/gitlab-runner-helper:x86_64-v16.11.2