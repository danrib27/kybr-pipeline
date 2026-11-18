locals {
  layers         = toset(["raw", "bronze", "silver", "gold"])
  athena_results = "s3://${var.data_bucket_name}/athena-results/"
}

resource "aws_s3_bucket" "data" {
  bucket        = var.data_bucket_name
  force_destroy = var.force_destroy
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Versioning keeps a paid copy of every overwritten object.
resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    id     = "expire-noncurrent-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }

  rule {
    id     = "remove-expired-delete-markers"
    status = "Enabled"

    filter {}

    expiration {
      expired_object_delete_marker = true
    }
  }

  rule {
    id     = "abort-incomplete-multipart-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # Rules on noncurrent versions need versioning enabled first.
  depends_on = [aws_s3_bucket_versioning.data]
}

# S3 has no folders: an empty "<layer>/" object shows it in the console.
resource "aws_s3_object" "layer" {
  for_each = local.layers

  bucket  = aws_s3_bucket.data.id
  key     = "${each.key}/"
  content = ""
}
