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

## How I Built It

### Stage 1 — Application
- Built a Flask registration web app with three routes: home, register, and success
- Replaced CSV file storage with DynamoDB for persistence across container restarts
- Replaced Gmail SMTP with AWS SES to work within ECS network restrictions
- Added a /health endpoint for ALB health checks
- Served with Gunicorn in production mode

### Stage 2 — Containerisation
- Wrote a Dockerfile using python:3.11-slim base image
- Installed dependencies separately from app code for better layer caching
- Runs as non-root user for security
- Built for linux/amd64 platform to run on ECS Fargate
- Pushed image to AWS ECR with lifecycle policy to keep last 5 images

### Stage 3 — Infrastructure as Code
All AWS infrastructure defined in Terraform across 9 files:

- **main.tf** — AWS provider and S3 remote state backend
- **variables.tf** — all configurable values
- **ecr.tf** — ECR repository with image scanning and lifecycle policy
- **dynamodb.tf** — DynamoDB table with pay-per-request billing
- **iam.tf** — least privilege IAM roles for ECS execution and task
- **networking.tf** — VPC, public subnets, internet gateway, ALB, security groups
- **ecs.tf** — Fargate cluster, task definition, and service with CloudWatch logging
- **cloudfront.tf** — global CDN distribution with static asset caching
- **outputs.tf** — app URL, CloudFront URL, cluster name, table name

### Stage 4 — CI/CD Pipeline
GitHub Actions workflow triggers on every push to main:

1. Checks out code
2. Authenticates with AWS using GitHub Secrets
3. Logs into ECR
4. Builds and pushes Docker image tagged with git SHA
5. Downloads current ECS task definition
6. Updates task definition with new image
7. Deploys to ECS Fargate and waits for stability
8. Invalidates CloudFront cache

### Security Practices
- All credentials stored as GitHub Secrets — never in source code
- IAM roles scoped to only the permissions the app needs
- ECS tasks only accept traffic from the load balancer
- CloudFront enforces HTTPS — HTTP redirects automatically
- DynamoDB and SES access restricted to the ECS task role only

## Deploy from Scratch

### Prerequisites
- AWS CLI configured
- Terraform installed
- Docker installed

### Steps

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

## Destroy Infrastructure

```bash
cd terraform
terraform destroy \
  -var="mail_username=your@gmail.com" \
  -var="mail_password=your_app_password"
```

## Author
Fayemi Abraham  Cloud & DevOps Engineer

GitHub: github.com/seed111
