output "data_bucket" {
  description = "Data lake bucket; s3.bucket_name in config.yaml."
  value       = aws_s3_bucket.data.bucket
}

output "athena_workgroup" {
  description = "Athena workgroup of the bronze jobs and dbt."
  value       = aws_athena_workgroup.pipeline.name
}

output "athena_results_location" {
  description = "Where Athena writes the query results."
  value       = local.athena_results
}

output "glue_databases" {
  description = "Glue databases of the medallion layers."
  value       = sort(keys(aws_glue_catalog_database.layer))
}

output "pipeline_policy_arn" {
  description = "ARN of the pipeline's least-privilege IAM policy."
  value       = aws_iam_policy.pipeline.arn
}

output "pipeline_user" {
  description = "IAM user the pipeline runs as."
  value       = aws_iam_user.pipeline.name
}
