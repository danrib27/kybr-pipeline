# Architecture Decision Records

## ADR-001: Replace staging/archive tables with Iceberg and partition-aware orchestration

- **Status:** Accepted; the orchestrator is amended by ADR-002
- **Date:** 2026-11-01

### Context

A common pattern in Hive-based data lakes processes each batch in four steps:
ingest raw files, load them into a temporary Hive external table, transform
with dbt, then move the temporary data into an archive table to record what has
been processed.

The staging and archive tables exist because Hive tables have no
transactions, no history and no notion of which data was already processed.
Batch tracking has to be implemented by hand.

### Decision

Use a three-step flow instead:

1. **Ingestion:** store original files, immutable, in the `raw/` zone on S3.
2. **Bronze:** load each raw partition into a permanent Apache Iceberg table,
   overwriting the partition on reprocessing and adding audit columns
   (`_ingested_at`, `_source_file`, `_batch_id`).
3. **dbt:** incremental models read new data from bronze and build facts and
   dimensions.

Processed-batch tracking comes from Dagster's per-partition materialization
history, row-level lineage from the audit columns, and rollback from Iceberg
snapshots.

### Alternatives considered

- **Staging + archive tables (Hive pattern):** proven, but adds an extra step
  and custom code to maintain for guarantees the table format now provides.
- **Delta Lake instead of Iceberg:** similar capabilities; Iceberg chosen for
  its engine-agnostic design and native support in AWS Glue and Athena.

### Consequences

- ✅ Fewer pipeline steps and less custom code.
- ✅ Idempotent reprocessing: rerunning a partition overwrites it.
- ✅ Trivial backfills through Dagster partitions.
- ✅ Point-in-time queries via Iceberg time travel.
- ⚠️ Requires understanding Iceberg snapshot management (expiring old
  snapshots to control storage costs).

## ADR-002: Orchestrate with Airflow instead of Dagster

- **Status:** Accepted
- **Date:** 2026-11-07
- **Amends:** ADR-001

### Context

ADR-001 relied on Dagster's per-partition materialization history to
track processed batches and on Dagster partitions for backfills.

Dagster was replaced because Apache Airflow is the orchestrator most
data teams run, and it has managed offerings (Amazon MWAA, Astronomer)
that run the same DAG files unchanged. A pipeline built on it shows
the skill most data engineering roles ask for, and its DAGs can move to
production without a rewrite.

### Decision

Orchestrate the pipeline with Apache Airflow 3. Each DAG run covers one
data interval (a month for `compras` and `licitacoes`, a day for `ceis`
and `cnep`), so processed-batch tracking comes from the DAG run history
and backfills from `airflow backfill create` over a date range. The
rest of ADR-001 holds: immutable files in `raw/`, Iceberg in bronze and
incremental dbt models.

Airflow runs locally in Docker, while the data and the queries live on
AWS (S3, Glue and Athena). The DAGs depend on nothing local, so they
are portable to MWAA or Astronomer.

### Alternatives considered

- **Dagster:** asset-based, with lineage between data assets built in,
  which Airflow lacks; less common in the job market and in managed
  cloud offerings.
- **Amazon MWAA:** the same Airflow, managed by AWS, but with a fixed
  cost of about US$ 365/month for the smallest environment, too much
  for a project that runs a few times a month.
- **AWS Step Functions:** AWS-native and pay per use, but with no
  built-in backfill or notion of a data interval; both would have to be
  written by hand.

### Consequences

- ✅ Idempotent reruns still come from overwriting the Iceberg
  partition of each data interval.
- ✅ No fixed orchestration cost: the local Airflow costs nothing.
- ⚠️ Airflow tracks task runs, not data assets: lineage between tables
  comes from dbt, not from the orchestrator.
- ⚠️ Schedules only run while the local Airflow is up; a missed run is
  caught up by a backfill.

## ADR-003: Use RustFS as the local S3

- **Status:** Accepted
- **Date:** 2026-11-07

### Context

Development and tests need an S3-compatible service on the local
machine, so the pipeline can run without an AWS account and without
paying for requests. The code talks to S3 through `boto3`, so any
service that implements the S3 API works by setting
`AWS_ENDPOINT_URL`.

### Decision

Run [RustFS](https://rustfs.com/) in `docker-compose.yml` as the local
S3, with one bucket holding the `raw/`, `bronze/` and `gold/`
prefixes, the same layout as on AWS.

### Alternatives considered

- **MinIO:** the usual choice, but its community edition was archived
  and no longer gets releases or images.
- **LocalStack:** emulates S3 and other AWS services, but its images
  now require an auth token, even for local use.

### Consequences

- ✅ The same code runs against RustFS and AWS; only the variables in
  `.env` change.
- ✅ No account, token or cost for local runs.
- ⚠️ RustFS is younger than MinIO; S3 features beyond objects and
  buckets may behave differently from AWS.

## ADR-004: One processing flow on AWS: Polars for bronze, Athena for dbt

- **Status:** Accepted
- **Date:** 2026-11-14

### Context

The bronze layer reads the raw zips and writes Iceberg tables, and dbt
builds the staging, intermediate and mart models on top of them. The
data sets are small: monthly files of a few megabytes and daily
snapshots, which fit in the memory of one machine.

Each SQL engine has its own dialect. If dbt ran on one engine in
development and another in production, a model could pass locally and
fail in production.

### Decision

Keep a single processing flow, on AWS:

- **Polars** does the bronze transformations, in single-machine Python
  jobs that write the Iceberg tables on S3.
- **Athena** is the only SQL engine for dbt (`dbt-athena`), with a
  `dev` and a `prod` target that write to separate Glue databases.
- **DuckDB** is only for ad-hoc exploration of the files and tables,
  outside the pipeline; no model or job depends on it.

### Alternatives considered

- **Apache Spark (EMR, Glue jobs or Databricks):** scales to data that
  does not fit one machine, but needs a cluster, its startup time and
  cost, and JVM tooling, for a volume that fits one machine.
- **dbt-duckdb for local development:** fast and free to run, but a
  second engine with another SQL dialect, so models could pass locally
  and fail on Athena.

### Consequences

- ✅ The models are developed and tested on the engine that runs them
  in production.
- ✅ Less infrastructure: the bronze jobs run in the Airflow worker or
  on a laptop, with no cluster to provision.
- ⚠️ Developing the dbt models needs AWS credentials and network
  access, and each run pays for the data Athena scans.
- ⚠️ If the volume outgrows one machine, the bronze jobs need to move
  to a distributed engine; the Iceberg tables stay as they are.
