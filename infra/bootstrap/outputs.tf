output "state_bucket" {
  description = "Bucket of the main stack's state; see its backend."
  value       = aws_s3_bucket.state.bucket
}
