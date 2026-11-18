variable "region" {
  description = "AWS region of every resource of the pipeline."
  type        = string
  default     = "us-east-1"
}

variable "data_bucket_name" {
  description = "Data lake bucket; s3.bucket_name in config.yaml."
  type        = string
  default     = "aws-s3-kybr"
}

variable "force_destroy" {
  description = <<-EOT
    Let `terraform destroy` delete the data bucket with its objects and
    versions. Apply it as true before destroying a non-empty bucket.
  EOT
  type        = bool
  default     = false
}

variable "pipeline_user_name" {
  description = "IAM user the pipeline runs as."
  type        = string
  default     = "kybr-pipeline"
}
