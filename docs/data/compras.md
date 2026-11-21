# compras

Contracts signed by the federal government, as registered in
ComprasNet. Source:
<https://portaldatransparencia.gov.br/download-de-dados/compras>.
Official dictionary:
<https://portaldatransparencia.gov.br/dicionario-de-dados/contratos>.

- **Cadence:** one zip per month, `YYYYMM_Compras.zip`.
- **Month cut:** `Data Publicação DOU`. Every row of `202606` was
  published in the DOU in June 2026, whatever its signature date.
- **Files:** `YYYYMM_Compras.csv`, `YYYYMM_ItemCompra.csv`,
  `YYYYMM_TermoAditivo.csv` and `YYYYMM_Apostilamento.csv`.
- **Format:** the common one, in the [index](README.md#file-format).

| File | Rows (2026-05, 06, 07) |
| --- | --- |
| `Compras` | 2,604; 1,749; 18 |
| `ItemCompra` | 8,932; 4,069; 47 |
| `TermoAditivo` | 42; 7; 2 |
| `Apostilamento` | 0; 0; 0 |

The meanings follow the official dictionary; the notes come from the
data. The column names are those of the CSV headers, which differ in
places from the dictionary's (`Data Início Vigência` there is
`Data Início da Vigência`, `Descrição Apostilamento` is `Descrição`).

## Organizational units

The government bodies come in three levels, as defined in the SIAFI
manual:

- **Órgão Superior:** a body of the direct administration that
  supervises other entities, as a ministry.
- **Órgão:** an entity supervised by an Órgão Superior, or the
  Órgão Superior itself.
- **Unidade Gestora (UG):** a budget or administrative unit that
  manages budget, money or assets, and whose head renders accounts
  every year (Decreto-lei 200/1967, arts. 81 and 82). Contracts and
  biddings are numbered within a UG.

## Relationships

```text
Compras (Código UG, Número do Contrato)
├── ItemCompra    (Código UG, Número Contrato)
└── TermoAditivo  (Código UG, Número Contrato)
```

Every `ItemCompra` row has its contract in `Compras` of the same
months. `Compras` points to its bidding in [licitacoes](licitacoes.md)
through `Número Licitação` and `Código UG Licitação`.

## Compras

One row per contract published in the month.

**Identifies a row:** none. `Código UG` + `Número do Contrato` is the
contract, but 63 contracts appear more than once with a different
`Objeto` or `Data Publicação DOU`. The same contract is published
again within a month, sometimes only to fix a typo in `Objeto`. See
[known issues](#known-issues).

| Column | Type | Meaning | Notes |
| --- | --- | --- | --- |
| `Número do Contrato` | string | number of the contract in ComprasNet | 9 digits: sequence (5) + year (4), as `000022026`; unique only within a UG |
| `Objeto` | string | object of the contract | always starts with `Objeto:`; up to 520 chars |
| `Fundamento Legal` | string | legal basis of the contract | starts with `Fundamento Legal:`; empty in 99.9% |
| `Modalidade Compra` | string | procurement modality | `Sem Informação` in 99%; see [modalities](#modalities) |
| `Situação Contrato` | string | status of the contract | always `Não se aplica` |
| `Código Órgão Superior` | string | Órgão Superior in charge of the bidding | 5 digits |
| `Nome Órgão Superior` | string | its name | |
| `Código Órgão` | string | Órgão in charge of the bidding | 5 digits |
| `Nome Órgão` | string | its name | cut at 45 chars, some with trailing spaces |
| `Código UG` | string | UG of the contract | 6 digits, leading zeros (`080001`) |
| `Nome UG` | string | its name | cut at 45 chars |
| `Data Assinatura Contrato` | date | signature of the contract | back to 2016 |
| `Data Publicação DOU` | date | publication of the contract in the DOU | defines the month of the file |
| `Data Início Vigência` | date | start of validity | |
| `Data Fim Vigência` | date | end of validity | empty in 2%; never before the start |
| `Código Contratado` | string | supplier's CNPJ, says the dictionary | also CPF (11 digits), 9-digit codes and `-11` when hidden |
| `Nome Contratado` | string | supplier's name | `Sigiloso` when hidden |
| `Valor Inicial Compra` | decimal(18,4) | initial value | 4 decimal places; `0,00` in 1% |
| `Valor Final Compra` | decimal(18,4) | final value, after adjustments, additions and the like | differs from the initial in 1% |
| `Número Licitação` | string | number of the bidding in SIASG, as in [licitacoes](licitacoes.md) | `-3` when there is none (60%) |
| `Código UG Licitação` | string | UG in charge of the bidding | filled in about 1% |
| `Nome UG Licitação` | string | its name | filled in about 1% |
| `Código Modalidade Compra Licitação` | string | modality code of the bidding | filled in about 1%; `5`, `6`, `7` or `9999` |
| `Modalidade Compra Licitação` | string | modality of the bidding | filled in about 1% |

## ItemCompra

One row per item of a contract.

**Identifies a row:** `Código UG` + `Número Contrato` +
`Código Item Compra`, except for hidden items (code `0`) and 11 other
collisions in the sample. There are also full-row duplicates (303 in
the sample).

| Column | Type | Meaning | Notes |
| --- | --- | --- | --- |
| `Código Órgão` | string | Órgão in charge of the bidding | |
| `Nome Órgão` | string | its name | cut at 45 chars |
| `Código UG` | string | UG of the contract | |
| `Nome UG` | string | its name | |
| `Número Contrato` | string | number of the contract in ComprasNet | joins `Compras.Número do Contrato` |
| `Código Item Compra` | string | code of the item in SIASG | 22 digits, see below; `0` when hidden |
| `Descrição Item Compra` | string | description of the item | hidden text when secret |
| `Descrição Complementar Item Compra` | string | free description | not in the dictionary; up to 1,300 chars |
| `Quantidade Item` | bigint | quantity | integer; `0` in a few rows |
| `Valor Item` | decimal(18,4) | **unit** value of the item | quantity × value adds up to `Valor Inicial Compra` in 96% of contracts |

`Código Item Compra` has 22 digits: `Código UG` (6) + modality (2,
see below) + number of the bidding in the year (5) + year of the
bidding (4) + item sequence within the bidding (5). Its first 6 digits
always match the `Código UG` of the row. As `Modalidade Compra` is
`Sem Informação` in 99% of contracts, these 2 digits are the best
source of the modality.

## Modalities

The modality comes as a name in `Compras.Modalidade Compra`, as a
code in `Código Modalidade Compra Licitação` and as 2 digits inside
`Código Item Compra`. The dictionary lists these codes:

| Code | Modality |
| --- | --- |
| `01` | Convite |
| `02` | Tomada de Preços |
| `03` | Concorrência |
| `04` | Concorrência Internacional |
| `05` | Pregão |
| `06` | Dispensa de Licitação |
| `07` | Inexigibilidade de Licitação |
| `20` | Concurso |
| `22` | Tomada de Preços por Técnica e Preço |
| `33` | Concorrência por Técnica e Preço |
| `44` | Concorrência Internacional por Técnica e Preço |
| `-99` | Pregão - Registro de Preços |

The data departs from this list. `Código Modalidade Compra Licitação`
has no leading zero (`5`, not `05`) and writes Pregão - Registro de
Preço as `9999`, not `-99`. Inside `Código Item Compra`, a price
registration has `05`, as any pregão; one item in the sample has
`99`.

## TermoAditivo

One row per amendment to a contract.

**Identifies a row:** `Código UG` + `Número Contrato` +
`Número Termo Aditivo`, unique in the sample.

| Column | Type | Meaning | Notes |
| --- | --- | --- | --- |
| `Número Contrato` | string | number of the contract in ComprasNet | |
| `Código Órgão Superior` | string | Órgão Superior in charge of the bidding | |
| `Nome Órgão Superior` | string | its name | |
| `Código Órgão` | string | Órgão in charge of the bidding | |
| `Nome Órgão` | string | its name | |
| `Código UG` | string | UG of the contract | |
| `Nome UG` | string | its name | |
| `Número Termo Aditivo` | string | number of the amendment in ComprasNet | 9 digits: sequence (5) + year (4) |
| `Data Publicação` | date | publication of the amendment in the DOU | empty in 12% |
| `Objeto` | string | object of the amendment | starts with `Objetivo:` |

## Apostilamento

One row per apostilamento: a change to a contract that the contract
already provides for, as a price adjustment, and so needs no
amendment. **Empty in every month of the sample**: the types come
from the dictionary and are not checked against data.

| Column | Type | Meaning |
| --- | --- | --- |
| `Número Contrato` | string | number of the contract in ComprasNet |
| `Código Órgão Superior` | string | Órgão Superior in charge of the bidding |
| `Nome Órgão Superior` | string | its name |
| `Código Órgão` | string | Órgão in charge of the bidding |
| `Nome Órgão` | string | its name |
| `Código UG` | string | UG of the contract |
| `Nome UG` | string | its name |
| `Número Apostilamento` | string | number of the apostilamento in ComprasNet |
| `Descrição Apostilamento` | string | description of the change |
| `Valor Apostilamento` | decimal(18,4) | value |
| `Data de inclusão` | date | date it was entered in ComprasNet |
| `Situação Apostilamento` | string | status: pendente, em encerramento, efetivado or encerrado |

## Known issues

- **Full-row duplicates:** 30 in `Compras` and 303 in `ItemCompra`.
- **Contracts published twice:** the same `Código UG` +
  `Número do Contrato` comes back with another `Objeto` (a fixed typo,
  as `PRETAÇÃO` → `PRESTAÇÃO`) or another `Data Publicação DOU`. Silver
  must pick one version.
- **Hidden contracts:** `Código Contratado` `-11`, `Nome Contratado`
  `Sigiloso` and the secret text in `Objeto` (about 1.5% of contracts);
  their items have code `0`.
- **Mostly empty columns:** `Fundamento Legal`, `Modalidade Compra`
  (`Sem Informação`), `Situação Contrato` (`Não se aplica`) and the
  bidding columns other than `Número Licitação`.
- **Modality codes off the dictionary:** `9999` instead of `-99`, and
  no leading zeros. See [modalities](#modalities).
- **Not only CNPJ:** the dictionary says `Código Contratado` is a
  CNPJ, but it also holds CPFs, 9-digit codes and `-11`.
- **Lost leading zero:** for a UG starting with `0`,
  `Código Item Compra` has 21 digits (16 rows). Pad it to 22 before
  splitting it.
- **Truncated names:** `Nome Órgão` and `Nome UG` are cut at 45
  characters, some with trailing spaces.
- **`Valor Item` differs from licitacoes:** here a unit value, there
  an item total.
- **Incomplete month:** `202607` has 18 contracts, against thousands
  in earlier months. The files of all three zips are dated 2026-07-07,
  so July was cut a week in: a month must be downloaded again once the
  portal completes it.
