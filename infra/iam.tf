data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

locals {
  partition    = data.aws_partition.current.partition
  account_id   = data.aws_caller_identity.current.account_id
  region_scope = "${var.region}:${local.account_id}"
  glue_arn     = "arn:${local.partition}:glue:${local.region_scope}"
  athena_arn   = "arn:${local.partition}:athena:${local.region_scope}"
  glue_db_list = keys(local.glue_databases)
}

data "aws_iam_policy_document" "pipeline" {
  statement {
    sid       = "ListDataBucket"
    actions   = ["s3:ListBucket", "s3:GetBucketLocation"]
    resources = [aws_s3_bucket.data.arn]
  }

  statement {
    sid = "ReadWriteDataObjects"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:AbortMultipartUpload",
      "s3:ListMultipartUploadParts",
    ]
    resources = ["${aws_s3_bucket.data.arn}/*"]
  }

  statement {
    sid = "RunAthenaQueries"
    actions = [
      "athena:StartQueryExecution",
      "athena:StopQueryExecution",
      "athena:GetQueryExecution",
      "athena:BatchGetQueryExecution",
      "athena:GetQueryResults",
      "athena:GetQueryRuntimeStatistics",
      "athena:ListQueryExecutions",
      "athena:GetWorkGroup",
    ]
    resources = [aws_athena_workgroup.pipeline.arn]
  }

  statement {
    sid       = "ReadAwsDataCatalog"
    actions   = ["athena:GetDataCatalog"]
    resources = ["${local.athena_arn}:datacatalog/AwsDataCatalog"]
  }

  # Glue authorizes each call on the catalog ARN as well as the
  # database and table ones.
  statement {
    sid = "ManagePipelineGlueTables"
    actions = [
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:GetTable",
      "glue:GetTables",
      "glue:CreateTable",
      "glue:UpdateTable",
      "glue:DeleteTable",
      "glue:BatchDeleteTable",
      "glue:GetTableVersion",
      "glue:GetTableVersions",
      "glue:DeleteTableVersion",
      "glue:BatchDeleteTableVersion",
      "glue:GetPartition",
      "glue:GetPartitions",
      "glue:BatchGetPartition",
      "glue:CreatePartition",
      "glue:BatchCreatePartition",
      "glue:UpdatePartition",
      "glue:BatchUpdatePartition",
      "glue:DeletePartition",
      "glue:BatchDeletePartition",
    ]
    resources = concat(
      ["${local.glue_arn}:catalog"],
      [for db in local.glue_db_list : "${local.glue_arn}:database/${db}"],
      [for db in local.glue_db_list : "${local.glue_arn}:table/${db}/*"],
    )
  }
}

resource "aws_iam_policy" "pipeline" {
  name        = "kybr-pipeline"
  description = "Least privilege for kybr-pipeline: S3, Athena and Glue."
  policy      = data.aws_iam_policy_document.pipeline.json
}

# No access key here: its secret would be stored in plain text in the
# state. Create it with the CLI (see CONTRIBUTING.md).
resource "aws_iam_user" "pipeline" {
  name = var.pipeline_user_name
}

resource "aws_iam_user_policy_attachment" "pipeline" {
  user       = aws_iam_user.pipeline.name
  policy_arn = aws_iam_policy.pipeline.arn
}
