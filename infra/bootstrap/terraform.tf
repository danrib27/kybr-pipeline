# The state bucket of infra/. Its own state stays local, since it
# cannot live in the bucket it creates; apply it once, before infra/.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.31"
    }
  }

  required_version = ">= 1.10"
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
