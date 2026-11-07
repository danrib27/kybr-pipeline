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

Python · AWS (S3, Glue, Athena) · Apache Iceberg · DuckDB / Polars · dbt ·
Airflow · Terraform · Docker · GitHub Actions

> **Status:** 🚧 work in progress. See the [roadmap](#roadmap) for what is
> already built.
