# compras

Contracts signed by the federal government, as registered in
ComprasNet. Source:
<https://portaldatransparencia.gov.br/download-de-dados/compras>.
Official dictionary:
<https://portaldatransparencia.gov.br/dicionario-de-dados/contratos>.

- **Cadence:** one zip per month, `YYYYMM_Compras.zip`.
- **Month cut:** `Data Publicação DOU`. Every row of `202403` was
  published in the DOU in March 2024, whatever its signature date.
  The amendments and apostilamentos of the zip are those of the
  month's contracts, whenever they were made, up to the download. See
  [known issues](#known-issues).
- **Files:** `YYYYMM_Compras.csv`, `YYYYMM_ItemCompra.csv`,
  `YYYYMM_TermoAditivo.csv` and `YYYYMM_Apostilamento.csv`.
- **Format:** the common one, in the [index](README.md#file-format).

| File | Rows (2024-02, 03, 04) |
| --- | --- |
| `Compras` | 2,527; 2,779; 2,722 |
| `ItemCompra` | 8,450; 11,480; 10,004 |
| `TermoAditivo` | 2,030; 2,013; 1,790 |
| `Apostilamento` | 14,452; 15,248; 13,078 |

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
├── ItemCompra     (Código UG, Número Contrato)
├── TermoAditivo   (Código UG, Número Contrato)
└── Apostilamento  (Código UG, Número Contrato)
```

Every `ItemCompra` and `TermoAditivo` row has its contract in
`Compras` of the same month. 203 of the 1,508 contracts in
`Apostilamento` are in no `Compras` file of the sample.

`Compras` points to its bidding in [licitacoes](licitacoes.md) through
the three columns that
[identify a bidding](licitacoes.md#licitação):

| `Compras` | `Licitação` |
| --- | --- |
| `Código UG Licitação` | `Código UG` |
| `Número Licitação` | `Número Licitação` |
| `Código Modalidade Compra Licitação` | `Código Modalidade Compra` |

The UG is `Código UG Licitação`, not `Código UG`: a contract can come
from another UG's bidding, as when a body joins another body's price
registration. That is the case of 20% of the contracts with a bidding,
mostly price registrations. A contract without a bidding,
`Número Licitação` `-3` or `-2` (27%), has nothing to join, nor have
48 others with a number but no UG or modality: 28% in all. How many of
the others find their bidding is not measured yet. See
[known issues](#known-issues).

The children join on `Código UG` + `Número Contrato` only, which does
not always tell one contract from another. See
[known issues](#known-issues).

## Compras

One row per contract published in the month.

**Identifies a row:** none. `Código UG` + `Número do Contrato` is
meant to be the contract, but 40 of them have more than one row (89
rows). In 36, the rows are different contracts, with different
suppliers, that share the number. In the other 4, the same contract
comes twice with another value, `Objeto` or end date. Adding
`Código Contratado` leaves only these 4. 25 of the 40 span more than
one month.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Número do Contrato` | `numero_do_contrato` | string | number of the contract in ComprasNet | 9 digits: sequence (5) + year (4), as `000012024`; not unique within a UG |
| `Objeto` | `objeto` | string | object of the contract | starts with `Objeto:`, or the secret text when hidden; up to 520 chars |
| `Fundamento Legal` | `fundamento_legal` | string | legal basis of the contract | starts with `Fundamento Legal:`; empty in 99% |
| `Modalidade Compra` | `modalidade_compra` | string | procurement modality | `Sem Informação` in 27%; see [modalities](#modalities) |
| `Situação Contrato` | `situacao_contrato` | string | status of the contract | `Não se aplica` in 99.5%; `Fechado` in 38, `Pendente` in 1 |
| `Código Órgão Superior` | `codigo_orgao_superior` | string | Órgão Superior in charge of the bidding | 5 digits |
| `Nome Órgão Superior` | `nome_orgao_superior` | string | its name | |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | 5 digits |
| `Nome Órgão` | `nome_orgao` | string | its name | cut at 45 chars, some with trailing spaces |
| `Código UG` | `codigo_ug` | string | UG of the contract | 6 digits, leading zeros (`080001`) |
| `Nome UG` | `nome_ug` | string | its name | cut at 45 chars |
| `Data Assinatura Contrato` | `data_assinatura_contrato` | date | signature of the contract | back to 2004; after the publication in 4 |
| `Data Publicação DOU` | `data_publicacao_dou` | date | publication of the contract in the DOU | defines the month of the file |
| `Data Início Vigência` | `data_inicio_vigencia` | date | start of validity | |
| `Data Fim Vigência` | `data_fim_vigencia` | date | end of validity | empty in 2%; before the start in 1 |
| `Código Contratado` | `codigo_contratado` | string | supplier's CNPJ, says the dictionary | also CPF (11 digits), 6- and 9-digit codes, `ESTRANGEIRO_<NAME>` and `-11` when hidden |
| `Nome Contratado` | `nome_contratado` | string | supplier's name | `Sigiloso` when hidden; empty in 2 |
| `Valor Inicial Compra` | `valor_inicial_compra` | decimal(18,4) | initial value | 4 decimal places; `0,00` in 1% |
| `Valor Final Compra` | `valor_final_compra` | decimal(18,4) | final value, after adjustments, additions and the like | differs from the initial in 29% |
| `Número Licitação` | `numero_licitacao` | string | number of the bidding in SIASG, as in [licitacoes](licitacoes.md) | `-3` when there is none (27%), `-2` in 39 |
| `Código UG Licitação` | `codigo_ug_licitacao` | string | UG in charge of the bidding | empty in 28% |
| `Nome UG Licitação` | `nome_ug_licitacao` | string | its name | empty in 28% |
| `Código Modalidade Compra Licitação` | `codigo_modalidade_compra_licitacao` | string | modality code of the bidding | empty in 28%; `1` to `7` or `9999` |
| `Modalidade Compra Licitação` | `modalidade_compra_licitacao` | string | modality of the bidding | empty in 28%; equals `Modalidade Compra` when filled |

## ItemCompra

One row per item of a contract.

**Identifies a row:** `Código UG` + `Número Contrato` +
`Código Item Compra`, except for hidden items (code `0`, 405 rows)
and 37 other collisions, where the same item comes with another
complementary description or value. As the contract number is not
unique, see [Compras](#compras), an item can belong to more than one
contract. There are also 27 full-row duplicates.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | |
| `Nome Órgão` | `nome_orgao` | string | its name | cut at 45 chars |
| `Código UG` | `codigo_ug` | string | UG of the contract | |
| `Nome UG` | `nome_ug` | string | its name | |
| `Número Contrato` | `numero_contrato` | string | number of the contract in ComprasNet | joins `Compras.Número do Contrato` |
| `Código Item Compra` | `codigo_item_compra` | string | code of the item in SIASG | 22 digits, see below; `0` when hidden |
| `Descrição Item Compra` | `descricao_item_compra` | string | description of the item | hidden text when secret |
| `Descrição Complementar Item Compra` | `descricao_complementar_item_compra` | string | free description | not in the dictionary; up to 1,224 chars |
| `Quantidade Item` | `quantidade_item` | bigint | quantity | integer; `0` in 193 rows, negative in 2 |
| `Valor Item` | `valor_item` | decimal(18,2) | **unit** value of the item | 2 decimal places; `0,00` in 339; quantity × value adds up to `Valor Final Compra` in 84% of contracts, to `Valor Inicial Compra` in 64% |

`Código Item Compra` has 22 digits: `Código UG` (6) + modality (2,
see below) + number of the bidding in the year (5) + year of the
bidding (4) + item sequence within the bidding (5). Its first 6 digits
always match the `Código UG` of the row, leading zero included.

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
Preço as `9999`, not `-99`. `Modalidade Compra` also has
Concorrência - Registro de Preço (2 contracts), which is in no list
and has no code. Inside `Código Item Compra`, a price registration
has `05`, as any pregão, and 95 items, all of contracts with
`Sem Informação`, have `99`.

## TermoAditivo

One row per amendment to a contract published in the month. The
amendments are those made up to the download, so a 2024 file has
amendments published up to 2026.

**Identifies a row:** `Código UG` + `Número Contrato` +
`Número Termo Aditivo`, except for 7 amendments that come twice with
another `Data Publicação` or `Objeto`. There is also 1 full-row
duplicate.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Número Contrato` | `numero_contrato` | string | number of the contract in ComprasNet | |
| `Código Órgão Superior` | `codigo_orgao_superior` | string | Órgão Superior in charge of the bidding | |
| `Nome Órgão Superior` | `nome_orgao_superior` | string | its name | |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | |
| `Nome Órgão` | `nome_orgao` | string | its name | |
| `Código UG` | `codigo_ug` | string | UG of the contract | |
| `Nome UG` | `nome_ug` | string | its name | |
| `Número Termo Aditivo` | `numero_termo_aditivo` | string | number of the amendment in ComprasNet | 9 digits: sequence (5) + year (4) |
| `Data Publicação` | `data_publicacao` | date | publication of the amendment in the DOU | empty in 2%; 2018 to 2026, and `28/03/3025` in 1 |
| `Objeto` | `objeto` | string | object of the amendment | starts with `Objetivo:`, or the secret text when hidden (140) |

## Apostilamento

An apostilamento is a change to a contract that the contract already
provides for, as a price adjustment, and so needs no amendment. Like
the amendments, the file has those of the month's contracts made up
to the download.

**Identifies a row:** none. Every row comes twice, once with
`Situação Apostilamento` `Não se aplica` and once with
`Nao se aplica`, which leaves 21,389 distinct rows. An apostilamento,
`Código UG` + `Número Contrato` + `Número Apostilamento`, then has 7
rows on average, up to 305, that differ only in
`Valor Apostilamento`, and no column tells them apart.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `Número Contrato` | `numero_contrato` | string | number of the contract in ComprasNet | |
| `Código Órgão Superior` | `codigo_orgao_superior` | string | Órgão Superior in charge of the bidding | `20101` or `20000` in 97%, not those of `Compras`; see [known issues](#known-issues) |
| `Nome Órgão Superior` | `nome_orgao_superior` | string | its name | `Sem informação` in 74% |
| `Código Órgão` | `codigo_orgao` | string | Órgão in charge of the bidding | matches `Compras` in 87% |
| `Nome Órgão` | `nome_orgao` | string | its name | upper case, unlike `Compras` |
| `Código UG` | `codigo_ug` | string | UG of the contract | `-3` in 30 rows |
| `Nome UG` | `nome_ug` | string | its name | `Inválido` when the UG is `-3` |
| `Número Apostilamento` | `numero_apostilamento` | string | number of the apostilamento in ComprasNet | `NNNNN/YYYY`, as `00001/2025`, unlike the other numbers |
| `Descrição Apostilamento` | `descricao_apostilamento` | string | description of the change | free text, up to 370 chars |
| `Valor Apostilamento` | `valor_apostilamento` | decimal(18,2) | value | 2 decimal places; `0,00` in 8%, negative in 4% |
| `Data de inclusão` | `data_de_inclusao` | date | date it was entered in ComprasNet | empty in 7%; 2021 to 2026 |
| `Situação Apostilamento` | `situacao_apostilamento` | string | status: pendente, em encerramento, efetivado or encerrado, says the dictionary | always `Não se aplica` or `Nao se aplica` |

## Known issues

- **Old months keep changing:** a zip holds the amendments and
  apostilamentos of its contracts up to the download, and
  `Valor Final Compra` reflects them: it differs from the initial
  value in 29% of the 2024 contracts. 3 contracts have a
  `Data Assinatura Contrato` of 2026-11-10, after their publication in
  2024. A month is never final: the bronze must keep the download
  date, and a month must be downloaded again to catch up.
- **Contract number not unique:** 36 `Código UG` +
  `Número do Contrato` pairs are shared by different contracts, with
  different suppliers. Items, amendments and apostilamentos join on
  those two columns only, so their contract is ambiguous there.
- **Contracts published twice:** 4 contracts come twice with another
  value, `Objeto` or end date, and 7 amendments with another date or
  `Objeto`. Silver must pick one version.
- **Full-row duplicates:** 4 in `Compras`, 27 in `ItemCompra` and 1 in
  `TermoAditivo`.
- **`Apostilamento` doubled:** each row comes with
  `Situação Apostilamento` `Não se aplica` and again with
  `Nao se aplica`. Once deduplicated, the rows of an apostilamento
  still differ only in value, with no column to tell them apart; it is
  unknown whether they add up.
- **`Apostilamento` units off the other files:**
  `Código Órgão Superior` is `20101` (`Sem informação`) or `20000`
  (Presidência da República) for most rows, and matches `Compras` for
  1% of them. `Código UG` is `-3`, with `Inválido` names, in 30 rows.
  Take the units from `Compras`.
- **Hidden contracts:** `Código Contratado` `-11`, `Nome Contratado`
  `Sigiloso` and the secret text in `Objeto` (138 contracts, 1.7%);
  the secret text also in 140 amendments. Their items have code `0`,
  as do 50 items of contracts that are not hidden.
- **Mostly empty columns:** `Fundamento Legal`, `Situação Contrato`
  (`Não se aplica`) and `Situação Apostilamento`. `Modalidade Compra`
  is `Sem Informação` and the bidding columns are empty in 28% of
  contracts: those without a bidding (`Número Licitação` `-3` or
  `-2`) and 48 with a bidding number only.
- **Modality codes off the dictionary:** `9999` instead of `-99`, no
  leading zeros, an extra Concorrência - Registro de Preço and `99`
  inside item codes. See [modalities](#modalities).
- **Not only CNPJ:** the dictionary says `Código Contratado` is a
  CNPJ, but it also holds CPFs, 6- and 9-digit codes,
  `ESTRANGEIRO_<NAME>` for foreign suppliers and `-11`.
- **Impossible dates:** an amendment published in `3025`, a contract
  that ends before it starts, 4 contracts signed after their
  publication and 48 amendments published before their contract.
- **Odd quantities and values:** `Quantidade Item` is negative in 2
  items and `0` in 193; `Valor Item` is `0,00` in 339;
  `Valor Apostilamento` is negative in 4%.
- **Truncated names:** `Nome Órgão` and `Nome UG` are cut at 45
  characters, some with trailing spaces.
- **Join to licitacoes not measured:** a bidding is homologated months
  before its contract is published, and the licitacoes file is cut by
  homologation date. The bidding of a contract in the sample can then
  be in a licitacoes file before 2024-02, which the sample lacks.
  Measuring the join's coverage needs the biddings of the months
  before the sample.
- **`Valor Item` differs from licitacoes:** here a unit value, there
  an item total.
- **Replaced characters:** 17 `¿` in `Fundamento Legal`, as
  `LEI N¿ 13.303/2016`.
