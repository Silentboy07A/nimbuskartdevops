variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "NimbusKart"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "devops-team"
}

variable "ssh_cidr" {
  description = "CIDR block allowed for SSH access"
  type        = string
  default     = "10.0.0.0/8"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "stopped_instance_days" {
  description = "Days threshold for stopped EC2 instances"
  type        = number
  default     = 14
}