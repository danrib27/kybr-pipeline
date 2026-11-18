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

variable "bytes_scanned_cutoff_per_query" {
  description = <<-EOT
    Bytes an Athena query may scan before it is cancelled (1 GiB). It
    protects the credits from a query without a filter that scans
    every table.
  EOT
  type        = number
  default     = 1073741824
}

variable "pipeline_user_name" {
  description = "IAM user the pipeline runs as."
  type        = string
  default     = "kybr-pipeline"
}
