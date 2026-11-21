# licitacoes

Biddings of the federal government, as registered in SIASG, with
their items and bidders. Source:
<https://portaldatransparencia.gov.br/download-de-dados/licitacoes>.
Official dictionary:
<https://portaldatransparencia.gov.br/dicionario-de-dados/licitacoes>.

- **Cadence:** one zip per month, `YYYYMM_Licitacoes.zip`.
- **Month cut:** `Data Resultado Compra`, the publication of the
  homologation in the DOU. Every row of `202403` was homologated in
  March 2024.
- **Files:** `YYYYMM_Licitação.csv`, `YYYYMM_ItemLicitação.csv`,
  `YYYYMM_ParticipantesLicitação.csv` and
  `YYYYMM_EmpenhosRelacionados.csv`. The names inside the zip have
  accents, unlike the zip.
- **Format:** the common one, in the [index](README.md#file-format).

| File | Rows (2024-02, 03, 04) |
| --- | --- |
| `Licitação` | 2,153; 2,653; 721 |
| `ItemLicitação` | 48,771; 57,381; 17,729 |
| `ParticipantesLicitação` | 163,976; 144,711; 38,737 |
| `EmpenhosRelacionados` | 0; 0; 0 |

The meanings follow the official dictionary; the notes come from the
data. The column names are those of the CSV headers, which differ in
places from the dictionary's (`Código Participante` there is
`CNPJ Participante`, `UF` and `Município` are one `UF/Município`).
Órgão Superior, Órgão and Unidade Gestora (UG) are explained in
[compras](compras.md#organizational-units).

## Relationships

```text
Licitação (Código UG, Número Licitação, Código Modalidade Compra)
├── ItemLicitação           (+ Código Item Compra, Código Vencedor)
├── ParticipantesLicitação  (+ Código Item Compra, Código Participante)
└── EmpenhosRelacionados    (same three columns)
```

Every `ItemLicitação` row has its bidding in `Licitação` of the same
months. The participants with `Flag Vencedor = SIM` are the winners in
`ItemLicitação`, with as many rows (123,881 of each): one per item,
or one per supplier for the 28 items split among suppliers.

## Licitação

One row per bidding homologated in the month.

**Identifies a row:** `Código UG` + `Número Licitação` +
`Código Modalidade Compra`, unique in the sample and across months.
`Número Licitação` alone repeats across UGs, and `Código UG` +
`Número Licitação` repeats across modalities.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Número Licitação` | `numero_licitacao` | string | number of the bidding in SIASG | 9 digits: number in the year (5) + year (4), as `000052023` |
| `Código UG` | `codigo_ug` | string | UG in charge of the bidding | 6 digits, leading zeros (`030100`) |
| `Nome UG` | `nome_ug` | string | its name | cut at 45 chars |
| `Código Modalidade Compra` | `codigo_modalidade_compra` | string | modality code | see [modalities](#modalities) |
| `Modalidade Compra` | `modalidade_compra` | string | modality | one name per code |
| `Número Processo` | `numero_processo` | string | process number of the bidding | free format: `08420010098202379`, `0375/2023`, `NÃO IDENTIFICADO` |
| `Objeto` | `objeto` | string | what is to be bought, sold or contracted | starts with `Objeto:`; up to 516 chars |
| `Situação Licitação` | `situacao_licitacao` | string | status of the bidding process | cut at 30 chars, as `Evento de Resultado de Julgame`; 21 values |
| `Código Órgão Superior` | `codigo_orgao_superior` | string | Órgão Superior in charge of the bidding | 5 digits |
| `Nome Órgão Superior` | `nome_orgao_superior` | string | its name | `Sem informação` in a few rows |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | 5 digits |
| `Nome Órgão` | `nome_orgao` | string | its name | cut at 45 chars, some with trailing spaces |
| `UF` | `uf` | string | state where the bidding takes place | 27 states, or `-3` |
| `Município` | `municipio` | string | city where the bidding takes place | mostly upper case without accents |
| `Data Resultado Compra` | `data_resultado_compra` | date | publication of the homologation in the DOU | defines the month of the file |
| `Data Abertura` | `data_abertura` | date | opening for proposals | empty in 27%; never after the result |
| `Valor Licitação` | `valor_licitacao` | decimal(18,4) | total value of the bidding | 4 decimal places; `0,00` in 44%, mostly price registrations |

## ItemLicitação

One row per item of a bidding and its winner.

**Identifies a row:** `Código UG` + `Número Licitação` +
`Código Modalidade Compra` + `Código Item Compra` + `Código Vencedor`,
unique for the rows with an item code. 480 rows have no item code and
no key. An item split among suppliers has a row per winner (28 items).
There are also 22 full-row duplicates.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Número Licitação` | `numero_licitacao` | string | number of the bidding in SIASG | |
| `Código UG` | `codigo_ug` | string | UG in charge of the bidding | |
| `Nome UG` | `nome_ug` | string | its name | |
| `Código Modalidade Compra` | `codigo_modalidade_compra` | string | modality code | |
| `Modalidade Compra` | `modalidade_compra` | string | modality | |
| `Número Processo` | `numero_processo` | string | process number of the bidding | |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | |
| `Nome Órgão` | `nome_orgao` | string | its name | cut at 45 chars |
| `Código Item Compra` | `codigo_item_compra` | string | code of the item in SIASG | 22 digits, see below; empty in 480 rows |
| `Descrição` | `descricao` | string | description of the item in SIASG | up to 120 chars |
| `Quantidade Item` | `quantidade_item` | bigint | quantity | integer |
| `Valor Item` | `valor_item` | decimal(18,4) | **total** value of the item | 4 decimal places; the items add up to `Valor Licitação` in 85% of biddings |
| `Código Vencedor` | `codigo_vencedor` | string | winner's CNPJ, says the dictionary | also CPF (11 digits) in 809 rows |
| `Nome Vencedor` | `nome_vencedor` | string | winner's name | sole traders as `53.068.544 NAME` |

`Código Item Compra` has 22 digits: `Código UG` (6) + modality (2) +
number of the bidding in the year (5) + year of the bidding (4) + item
sequence within the bidding (5). The middle 9 digits are
`Número Licitação`. For `155126 05 00036 2023 00053`, the UG is
`155126` and the bidding `000362023`.

## ParticipantesLicitação

One row per bidder of an item.

**Identifies a row:** `Código UG` + `Número Licitação` +
`Código Modalidade Compra` + `Código Item Compra` +
`Código Participante`, unique except for the hidden bidders (`-11`).
There are also 1,419 full-row duplicates.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Número Licitação` | `numero_licitacao` | string | number of the bidding in SIASG | |
| `Código UG` | `codigo_ug` | string | UG in charge of the bidding | |
| `Nome UG` | `nome_ug` | string | its name | |
| `Código Modalidade Compra` | `codigo_modalidade_compra` | string | modality code | |
| `Modalidade Compra` | `modalidade_compra` | string | modality | |
| `Número Processo` | `numero_processo` | string | process number of the bidding | |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | |
| `Nome Órgão` | `nome_orgao` | string | its name | cut at 45 chars |
| `Código Item Compra` | `codigo_item_compra` | string | code of the item in SIASG | `0` when hidden |
| `Descrição Item Compra` | `descricao_item_compra` | string | description of the item in SIASG | hidden text when secret |
| `Código Participante` | `codigo_participante` | string | bidder's CNPJ, says the dictionary | also CPF (11 digits); `-11` when hidden |
| `Nome Participante` | `nome_participante` | string | bidder's name | `Sigiloso` when hidden |
| `Flag Vencedor` | `flag_vencedor` | string | whether the bidder won the item | `SIM` or `NÃO` |

## EmpenhosRelacionados

Commitments of expense (empenhos) of a bidding. **Empty in every
month of the sample**: the types come from the dictionary and are not
checked against data.

| Column | Bronze name | Type | Meaning |
| --- | --- | --- | --- |
| `Número Licitação` | `numero_licitacao` | string | number of the bidding in SIASG |
| `Código UG` | `codigo_ug` | string | UG in charge of the bidding |
| `Nome UG` | `nome_ug` | string | its name |
| `Código Modalidade Compra` | `codigo_modalidade_compra` | string | modality code |
| `Modalidade Compra` | `modalidade_compra` | string | modality |
| `Número Processo` | `numero_processo` | string | process number of the bidding |
| `Código Empenho` | `codigo_empenho` | string | code of the commitment |
| `Data Emissão Empenho` | `data_emissao_empenho` | date | date the commitment was issued |
| `Observação Empenho` | `observacao_empenho` | string | notes on the commitment |
| `Valor Empenho (R$)` | `valor_empenho_brl` | decimal(18,4) | value of the commitment; scale unchecked, as the file is empty |

## Modalities

The dictionary lists the codes of [compras](compras.md#modalities).
The data has 7 of them, without leading zeros, and Pregão - Registro
de Preço as `9999` instead of `-99`:

| `Código Modalidade Compra` | `Modalidade Compra` | In `Código Item Compra` |
| --- | --- | --- |
| `1` | Convite | `01` |
| `2` | Tomada de Preços | `02` |
| `3` | Concorrência | `03` |
| `5` | Pregão | `05` |
| `6` | Dispensa de Licitação | `06` |
| `7` | Inexigibilidade de Licitação | `07` |
| `9999` | Pregão - Registro de Preço | `05` |

## Known issues

- **Full-row duplicates:** 22 in `ItemLicitação` and 1,419 in
  `ParticipantesLicitação`.
- **Items without a code:** 480 `ItemLicitação` rows have an empty
  `Código Item Compra`, so they cannot be told apart or joined to
  their bidders.
- **Lost leading zero:** for a UG starting with `0`, as `080001`,
  `Código Item Compra` has 21 digits (`80001…`). Pad it to 22 before
  splitting it.
- **Modality codes off the dictionary:** `9999` instead of `-99`, and
  no leading zeros. A price registration has `05` inside the item
  code, so the item code cannot tell it from a plain pregão.
- **Not only CNPJ:** the dictionary says `Código Vencedor` and
  `Código Participante` are CNPJs, but they also hold CPFs.
- **Hidden bidders:** `Código Participante` `-11`, `Nome Participante`
  `Sigiloso`, item code `0` and the secret text as the description.
- **`UF` placeholder:** `-3` for biddings with no state.
- **Truncated text:** `Situação Licitação` cut at 30 characters,
  `Nome Órgão` and `Nome UG` at 45, some with trailing spaces.
- **Zero values:** `Valor Licitação` is `0,00` in 44% of biddings,
  mostly price registrations (`9999`); take the value from the items.
- **`Valor Item` differs from compras:** here an item total, there a
  unit value.
- **Short month:** `202404` covers only 2024-04-01 to 2024-04-05
  (721 biddings, against 2,153 and 2,653 in the months before).
- **Replaced characters:** 90 `¿` in `Objeto` in the sample, where
  the source had a character outside latin-1.
