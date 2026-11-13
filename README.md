# kybr-pipeline

**Supplier risk scoring lakehouse built on Brazilian public data.**

kybr-pipeline is a Know-Your-Business (KYB) pipeline: is an end-to-end data
platform that cross-references Brazil's federal company registry, public
procurement records and government sanction lists to flag high-risk government
suppliers.

## What it answers

- Is a company that just won a public contract currently sanctioned?
- Does it share partners with other suppliers of the same government agency?
- Was it incorporated only a few months before winning a high-value tender?

## Data sources

| Source | Dataset | Publisher |
| --- | --- | --- |
| Company registry | CNPJ open data (companies, establishments, partners) | Receita Federal |
| Public procurement | Tenders and contracts | Portal da Transparência (CGU) |
| Sanctions | CEIS (debarred companies) and CNEP (companies punished under the Anti-Corruption Law) | Portal da Transparência (CGU) |

## Tech stack

Today the code uses:

- **Python 3.12** with `requests` and `boto3`, managed with `uv`
- **AWS S3** for the raw zone, with **RustFS** as the local S3 in
  development
- **Docker Compose** for the local services
- **GitHub Actions** running Ruff and pytest on every pull request

The tools still to come are in the [roadmap](#roadmap).

> **Status:** 🚧 work in progress. See the [roadmap](#roadmap) for what is
> already built.

## Roadmap

### Done

- [x] Ingestion of the Portal da Transparência data sets into the `raw/`
  zone on S3: monthly ones (`compras`, `licitacoes`) by a range of
  months, and the daily snapshots (`ceis`, `cnep`) with a fallback to
  yesterday
- [x] Retries with exponential backoff for transient HTTP errors
  ([#3](https://github.com/danrib27/kybr-pipeline/issues/3))
- [x] Progress logs for each download and upload
  ([#4](https://github.com/danrib27/kybr-pipeline/issues/4))
- [x] CI with lint and tests on every pull request

### Next

- [ ] Backfill the raw history of every data set
  ([#7](https://github.com/danrib27/kybr-pipeline/issues/7))
- [ ] Provision the bucket and IAM with **Terraform**
  ([#9](https://github.com/danrib27/kybr-pipeline/issues/9))
- [ ] Load the raw zips into **Apache Iceberg** bronze tables, queried
  through **AWS Glue** and **Athena**, with **DuckDB / Polars**
  ([#11](https://github.com/danrib27/kybr-pipeline/issues/11))
- [ ] Ingest the CNPJ registry from Receita Federal
  ([#12](https://github.com/danrib27/kybr-pipeline/issues/12))
- [ ] Build the staging, intermediate and supplier risk mart with
  **dbt** ([#13](https://github.com/danrib27/kybr-pipeline/issues/13))
- [ ] Run the pipeline as **Airflow** DAGs
  ([#14](https://github.com/danrib27/kybr-pipeline/issues/14))
- [ ] Data quality checks and LGPD notes
  ([#15](https://github.com/danrib27/kybr-pipeline/issues/15))

The design decisions are recorded in the
[architecture decision records](docs/decisions.md).
