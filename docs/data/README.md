# Data dictionary

One page per data set of the [Portal da Transparência][portal]. Each
page is the source schema of its bronze tables: the files inside
each zip, their columns with type and meaning, the columns that
identify a row and the known data quality issues.

| Data set | Cadence | Files in the zip |
| --- | --- | --- |
| [compras](compras.md) | monthly | `Compras`, `ItemCompra`, `TermoAditivo`, `Apostilamento` |
| [licitacoes](licitacoes.md) | monthly | `Licitação`, `ItemLicitação`, `ParticipantesLicitação`, `EmpenhosRelacionados` |
| [ceis](ceis.md) | daily snapshot | `CEIS` |
| [cnep](cnep.md) | daily snapshot | `CNEP` |

## How the pages were written

The facts come from profiling the raw zips, all values read as text:
`compras` 2026-05 to 2026-07, `licitacoes` 2024-02 to 2024-04, and the
`ceis` and `cnep` snapshots of 2026-11-19. Counts on the pages are from
that sample.

The meaning of a column follows the portal's official dictionary,
linked on each page. Where the data departs from the dictionary, the
page says so. The column names are those of the CSV headers, which
are what the bronze reads, and differ in places from the
dictionary's.

## File format

Every CSV of the four data sets has the same format:

| Property | Value |
| --- | --- |
| Encoding | ISO-8859-1 (latin-1), no BOM |
| Separator | `;` |
| Quoting | every field, header included, in `"` |
| Line ending | CRLF; no line breaks inside fields |
| Header | one line, column names in Portuguese with accents |
| Empty value | `""`, an empty quoted string, never a missing field |
| Date | `dd/mm/yyyy` |
| Decimal | comma, no thousands separator: `428400,9600` |

Characters outside latin-1 are replaced by `¿` at the source, as in
`CONTRATO N¿ 7`.

## Names

Each column keeps its source name, as in the CSV header, and gets a
bronze name in snake_case, as the notebooks' `to_snake_case` builds
it:

1. `(R$)` becomes the `_brl` suffix.
2. Accents are stripped and letters lowercased.
3. Any run of characters other than letters and digits, as a space or
   ` - `, becomes one `_`.

So `Valor Empenho (R$)` is `valor_empenho_brl`, and
`RAZÃO SOCIAL - CADASTRO RECEITA` is `razao_social_cadastro_receita`.
The bronze names are unique within each file.

## Types

The bronze type is the Iceberg type a column gets when read with the
format above:

- `string`: codes and identifiers too, since they carry leading zeros
  (`000022026`, `03000`, CPF and CNPJ) that a number would drop.
- `bigint`: counts, such as a quantity.
- `decimal(18,2)` or `decimal(18,4)`: money, in BRL, with the scale
  the source writes, so no value is rounded. A column written with 4
  decimal places (`428400,9600`) is `decimal(18,4)`, even where a
  zero comes as `0,00`; one written with 2 (`3,36`) is
  `decimal(18,2)`. A file that came empty in the sample gets
  `decimal(18,4)`, which loses nothing whatever its real scale.
- `date`: parsed from `dd/mm/yyyy`.

An empty string becomes null in every type.

## Placeholder values

The portal fills unknown or hidden values with placeholders instead of
leaving them empty. They are listed on each page and must become null,
or a flag, before any count or join:

| Value | Meaning |
| --- | --- |
| `-11` (code), `Sigiloso` (name) | supplier hidden by secrecy |
| `Informação protegida por sigilo nos termos da legislação vigente` | description hidden by secrecy |
| `-3` | not informed |
| `Sem Informação`, `Sem informação`, `SEM INFORMACAO` | not informed |
| `Não se aplica` | not applicable |

[portal]: https://portaldatransparencia.gov.br/download-de-dados
