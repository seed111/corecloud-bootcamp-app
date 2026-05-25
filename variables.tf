variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "app_name" {
  description = "Application name used for naming resources"
  type        = string
  default     = "corecloud-bootcamp"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "mail_username" {
  description = "Gmail username for sending emails"
  type        = string
  sensitive   = true
}

variable "mail_password" {
  description = "Gmail app password"
  type        = string
  sensitive   = true
}

variable "admin_email" {
  description = "Admin email to receive registration notifications"
  type        = string
  default     = "corecloud.info@gmail.com"
}

variable "container_port" {
  description = "Port the Flask app runs on inside the container"
  type        = number
  default     = 5000
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}
