provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "GameX"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}