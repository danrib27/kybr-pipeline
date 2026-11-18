terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.31"
    }
  }

  # use_lockfile needs 1.10.
  required_version = ">= 1.10"

  # A backend cannot read variables: keep the bucket in sync with
  # infra/bootstrap and the region with var.region.
  backend "s3" {
    bucket       = "aws-s3-kybr-tfstate"
    key          = "kybr-pipeline/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = "kybr-pipeline"
      ManagedBy = "terraform"
    }
  }
}
