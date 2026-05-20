resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.20.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name        = "${var.project}-public-a"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.20.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name        = "${var.project}-public-b"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}