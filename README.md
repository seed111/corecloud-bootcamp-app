# CoreCloud Bootcamp App

> A production-grade web application for managing bootcamp student registrations, built and deployed on AWS using modern DevOps practices. The entire infrastructure deploys from scratch with a single Terraform command and tears down just as easily to avoid unnecessary costs.

[![Live App](https://img.shields.io/badge/Live%20App-CloudFront-blue?style=flat-square)](https://d2vd2uz8mfrvi7.cloudfront.net)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-purple?style=flat-square)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/Cloud-AWS-orange?style=flat-square)](https://aws.amazon.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black?style=flat-square)](https://github.com/features/actions)

**Live App:** https://d2vd2uz8mfrvi7.cloudfront.net

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [How I Built It](#how-i-built-it)
4. [Terraform Files](#terraform-files)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [IAM Roles and Privileges](#iam-roles-and-privileges)
7. [Security Practices](#security-practices)
8. [Deploy from Scratch](#deploy-from-scratch)
9. [Destroy Infrastructure](#destroy-infrastructure)
10. [Cost](#cost)
11. [What Was Learned](#what-was-learned)

---

## Architecture Overview

```
Student Browser
      ↓
CloudFront (Global CDN — 400+ edge locations worldwide)
      ↓
Application Load Balancer (eu-west-1)
      ↓
ECS Fargate (Serverless containers)
      ↓
Flask App (Python + Gunicorn)
      ↓
DynamoDB (Registration data) + SES (Email alerts)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python, Flask, Gunicorn |
| Containerisation | Docker, AWS ECR |
| Hosting | AWS ECS Fargate |
| Database | AWS DynamoDB |
| Email | AWS SES |
| CDN | AWS CloudFront |
| Networking | VPC, Subnets, ALB, Security Groups |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |
| Security | IAM least privilege, env vars, GitHub Secrets |

---

## How I Built It

The project was built in four stages. Each stage built on top of the previous one.

### Stage 1 — Application

Flask was chosen because it is lightweight and easy to deploy inside a container. The app has three routes — home, register and success. When a student submits the registration form the data goes straight to DynamoDB and an email notification is sent via AWS SES.

CSV file storage was replaced with DynamoDB because containers are ephemeral. Every time ECS restarts a task the local filesystem is wiped clean. DynamoDB lives outside the container so registrations are never lost.

Gmail SMTP was replaced with AWS SES because ECS Fargate blocks outbound SMTP connections on port 465. SES uses the AWS SDK internally which works perfectly inside the ECS network. It is also the more professional and scalable solution for sending email from AWS infrastructure.

A /health endpoint was added because the Application Load Balancer needs it to check whether the container is running correctly before sending traffic to it. Without this endpoint the ALB marks the task as unhealthy and takes it out of rotation.

Gunicorn was used instead of the Flask development server because the Flask dev server is single-threaded and not suitable for production. Gunicorn handles multiple requests concurrently and is the standard way to serve Flask apps in production.

### Stage 2 — Containerisation

The python:3.11-slim base image was chosen to keep the container as small as possible. Slim images have fewer packages installed which reduces the attack surface and speeds up pull times on ECS.

Dependencies are copied and installed before the application code. This is a Docker layer caching optimisation. When only the application code changes Docker reuses the cached layer where dependencies were installed instead of reinstalling everything from scratch. This makes subsequent builds significantly faster.

The container runs as a non-root user called appuser. Running as root inside a container is a security risk. If someone exploited a vulnerability in the application they would have root access inside the container. Running as a non-root user limits what an attacker can do.

The image is built for the linux/amd64 platform explicitly. This project was developed on a Mac with an Apple Silicon chip which uses the ARM architecture. ECS Fargate runs on AMD64. Without specifying the platform the container crashes silently on ECS with no useful error message.

Images are pushed to AWS ECR with a lifecycle policy that keeps only the last five images. This prevents the registry from filling up with old unused images and keeps storage costs low.

### Stage 3 — Infrastructure as Code

All AWS infrastructure is defined in Terraform across nine files. Each file handles one area of concern which makes the infrastructure easier to read, maintain and debug. Details of each file are in the [Terraform Files](#terraform-files) section below.

### Stage 4 — CI/CD Pipeline

GitHub Actions was chosen because the code is already on GitHub and the integration is seamless. No additional tools or accounts are needed. Details of the pipeline steps are in the [CI/CD Pipeline](#cicd-pipeline) section below.

---

## Terraform Files

All nine files live inside the `terraform/` folder.

| File | What It Does |
|---|---|
| `main.tf` | AWS provider and S3 remote state backend |
| `variables.tf` | All configurable values including sensitive credentials |
| `ecr.tf` | Container registry with image scanning and lifecycle policy |
| `dynamodb.tf` | Registrations table with pay-per-request billing |
| `iam.tf` | Least privilege IAM roles for ECS execution and task |
| `networking.tf` | VPC, subnets, internet gateway, ALB, security groups |
| `ecs.tf` | Fargate cluster, task definition, service, CloudWatch logs |
| `cloudfront.tf` | Global CDN distribution with static asset caching |
| `outputs.tf` | App URL, CloudFront URL, cluster name, table name |

**main.tf** sets up the AWS provider and configures the S3 remote backend for Terraform state. Storing state remotely means the CI/CD pipeline can access it from anywhere and multiple people can work on the infrastructure without conflicts.

**variables.tf** defines all configurable values in one place. Sensitive values like email credentials are marked as sensitive so Terraform never prints them in logs or plan output.

**ecr.tf** creates the container registry where Docker images are stored. Image scanning is enabled on push so any known vulnerabilities in the image are flagged automatically. The lifecycle policy keeps only the last five images to control storage costs.

**dynamodb.tf** creates the registrations table with pay-per-request billing. This means there is no minimum cost and the table scales automatically with traffic without any capacity planning needed.

**iam.tf** creates two IAM roles. The ECS execution role allows ECS to pull images from ECR and write logs to CloudWatch. The ECS task role gives the running application permission to write to DynamoDB and send email via SES. Both roles follow the principle of least privilege.

**networking.tf** builds the entire network layer. The VPC gives the infrastructure its own isolated network. Two public subnets across two availability zones provide redundancy. The internet gateway allows traffic in and out. The Application Load Balancer sits in front of the ECS tasks. Two security groups control the traffic — one for the load balancer that accepts HTTP from anywhere, and one for the ECS tasks that only accepts traffic from the load balancer.

**ecs.tf** defines the Fargate cluster, task definition and service. The task definition specifies the container image, CPU and memory allocation, environment variables and log configuration. The service maintains the desired number of running tasks and replaces any that become unhealthy.

**cloudfront.tf** creates a global CDN distribution in front of the load balancer. Static assets are cached at edge locations for up to seven days. Dynamic pages pass through to the origin with no caching so form submissions always reach the application. HTTPS is enforced automatically.

**outputs.tf** prints the app URL, CloudFront URL, ECS cluster name and DynamoDB table name after deployment so everything is easy to find without going into the AWS console.

---

## CI/CD Pipeline

The pipeline lives in `.github/workflows/deploy.yml` and triggers on every push to the main branch.

| Step | Action |
|---|---|
| 1 | Checks out the latest code from GitHub |
| 2 | Authenticates with AWS using GitHub Secrets |
| 3 | Logs into AWS ECR |
| 4 | Builds Docker image tagged with the git commit SHA |
| 5 | Pushes the image to ECR as both SHA tag and latest |
| 6 | Downloads the current ECS task definition |
| 7 | Updates the task definition with the new image tag |
| 8 | Deploys to ECS Fargate and waits for service stability |
| 9 | Invalidates CloudFront cache across all edge locations |

Tagging with the git SHA means every image is traceable back to the exact commit that produced it. Waiting for service stability means a failed deployment is caught immediately rather than silently replacing a working version.

---

## IAM Roles and Privileges

Two IAM roles were created for this system. Each one has only the permissions it needs and nothing more.

### ECS Execution Role

This role is used by ECS itself to set up the container before it starts running. It needs permission to pull the Docker image from ECR using `ecr:GetAuthorizationToken` and `ecr:BatchGetImage`. It also needs permission to write logs to CloudWatch using `logs:CreateLogGroup`, `logs:CreateLogStream` and `logs:PutLogEvents`. The AWS managed policy `AmazonECSTaskExecutionRolePolicy` covers all of these and nothing more.

### ECS Task Role

This role is used by the running Flask application inside the container. It needs permission to write new registrations to DynamoDB using `dynamodb:PutItem` scoped to the specific registrations table only. It needs permission to send email via SES using `ses:SendEmail` and `ses:SendRawEmail`. No other permissions are granted.

### What Was Not Granted

The application cannot read, update or delete existing DynamoDB records. It cannot access S3, EC2, CloudTrail or any other AWS service. ECS tasks only accept traffic from the load balancer security group. Direct access from the internet is blocked at the network level.

---

## Security Practices

All credentials are stored as GitHub Secrets and injected as environment variables at runtime. They are never written in source code or Terraform files. CloudFront enforces HTTPS and redirects all HTTP traffic automatically. The S3 bucket holding Terraform state is private with versioning enabled. ECS tasks run as non-root users inside the container.

---

## Deploy from Scratch

**Prerequisites**

- AWS CLI configured
- Terraform installed
- Docker installed

**Steps**

```bash
# 1. Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket corecloud-terraform-state \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply \
  -var="mail_username=your@gmail.com" \
  -var="mail_password=your_app_password"

# 3. Build and push Docker image
cd ..
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com

docker buildx build \
  --platform linux/amd64 \
  -t YOUR_ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/corecloud-bootcamp:latest \
  --push .

# 4. Force ECS to pick up the new image
aws ecs update-service \
  --cluster corecloud-bootcamp-cluster \
  --service corecloud-bootcamp-service \
  --force-new-deployment \
  --region eu-west-1
```

---

## Destroy Infrastructure

```bash
cd terraform
terraform destroy \
  -var="mail_username=your@gmail.com" \
  -var="mail_password=your_app_password"
```

---

## Cost

The main running costs are ECS Fargate tasks, the Application Load Balancer and CloudFront requests. At low traffic the monthly cost is approximately two to five dollars. Destroying the infrastructure when not in use brings the cost to zero.

---

## What Was Learned

Building the Docker image for the wrong platform was the biggest challenge. The container ran perfectly on the Mac but crashed silently on ECS Fargate with no logs. The fix was specifying the linux/amd64 platform explicitly in the build command.

ECS Fargate blocks outbound SMTP connections which caused the email feature to fail in production even though it worked locally. Switching to AWS SES solved this and is the correct approach for sending email from AWS infrastructure.

Splitting Terraform into nine separate files made the infrastructure much easier to reason about and debug compared to putting everything in a single file.

---

## Author

**Fayemi Abraham** — Cloud & DevOps Engineer

[![GitHub](https://img.shields.io/badge/GitHub-seed111-black?style=flat-square&logo=github)](https://github.com/seed111)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fayemi%20Abraham-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/abraham-fayemi-0032382a0)
