# CoreCloud Bootcamp App

A production-grade Flask web application deployed on AWS using Docker, ECS Fargate, and Terraform.

## Architecture
- **Flask** — Python web application
- **Docker** — containerised application
- **AWS ECR** — container image registry
- **AWS ECS Fargate** — serverless container hosting
- **AWS DynamoDB** — registrations database
- **AWS SES** — email notifications
- **AWS CloudFront** — global CDN
- **Terraform** — infrastructure as code
- **GitHub Actions** — CI/CD pipeline

## Live App
https://d2vd2uz8mfrvi7.cloudfront.net

## How it works
1. Student fills in registration form
2. Data saved to DynamoDB
3. Email notification sent via SES
4. CloudFront serves the app globally

## Infrastructure
All infrastructure is defined in Terraform and deployable from scratch:
```bash
cd terraform
terraform init
terraform apply
```

## CI/CD
Every push to main automatically:
1. Builds a new Docker image
2. Pushes to ECR
3. Deploys to ECS Fargate
4. Invalidates CloudFront cache
