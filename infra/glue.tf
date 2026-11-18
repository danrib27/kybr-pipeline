# dbt's dev target writes to the dev_ databases, so it never
# overwrites the prod tables (ADR-004).
locals {
  glue_databases = {
    bronze     = "bronze/"
    silver     = "silver/"
    gold       = "gold/"
    dev_silver = "silver/dev/"
    dev_gold   = "gold/dev/"
  }
}

resource "aws_glue_catalog_database" "layer" {
  for_each = local.glue_databases

  name         = each.key
  description  = "kybr-pipeline: ${each.key} layer"
  location_uri = "s3://${aws_s3_bucket.data.bucket}/${each.value}"
}
