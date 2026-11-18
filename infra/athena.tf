resource "aws_athena_workgroup" "pipeline" {
  name        = "kybr-pipeline"
  description = "Queries of the bronze jobs and dbt."

  # Otherwise `terraform destroy` fails on the saved queries.
  force_destroy = true

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = false
    bytes_scanned_cutoff_per_query     = var.bytes_scanned_cutoff_per_query

    # Pinned, so an AWS upgrade does not change the SQL under dbt.
    engine_version {
      selected_engine_version = "Athena engine version 3"
    }

    result_configuration {
      output_location = local.athena_results

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
}
