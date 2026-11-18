variable "region" {
  description = "AWS region of the state bucket."
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Name of the bucket that holds the Terraform state."
  type        = string
  default     = "aws-s3-kybr-tfstate"
}
