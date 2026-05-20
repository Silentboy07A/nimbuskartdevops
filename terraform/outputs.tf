output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "subnet_public_a_id" {
  description = "Public Subnet A ID"
  value       = module.network.subnet_public_a_id
}

output "subnet_public_b_id" {
  description = "Public Subnet B ID"
  value       = module.network.subnet_public_b_id
}

output "bucket_name" {
  description = "S3 bucket name for app logs"
  value       = aws_s3_bucket.logs.bucket
}

output "web_instance_ids" {
  description = "Web tier EC2 instance IDs"
  value       = aws_instance.web[*].id
}

output "orphan_ebs_volume_id" {
  description = "Orphan EBS volume ID for testing"
  value       = aws_ebs_volume.orphan.id
}