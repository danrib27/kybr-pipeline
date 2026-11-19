# dev_ is dbt's dev target (ADR-004). Its prefixes sit beside the prod
# ones, so cleaning a prod prefix never touches dev data.
locals {
  glue_databases = {
    bronze     = "bronze/"
    silver     = "silver/"
    gold       = "gold/"
    dev_silver = "dev_silver/"
    dev_gold   = "dev_gold/"
  }
}

resource "aws_glue_catalog_database" "layer" {
  for_each = local.glue_databases

  name         = each.key
  description  = "kybr-pipeline: ${each.key} layer"
  location_uri = "s3://${aws_s3_bucket.data.bucket}/${each.value}"
}
