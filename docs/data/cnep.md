# cnep

Cadastro Nacional de Empresas Punidas: companies punished under the
Anti-Corruption Law (Lei 12.846/2013), by any federal, state or
municipal body. Source:
<https://portaldatransparencia.gov.br/download-de-dados/cnep>.
Official dictionary:
<https://portaldatransparencia.gov.br/dicionario-de-dados/cnep>.

- **Cadence:** a daily snapshot, `YYYYMMDD_CNEP.zip`, of the whole
  register. Only the latest one is kept, so a sanction that leaves the
  register leaves the data.
- **Files:** `YYYYMMDD_CNEP.csv`.
- **Format:** the common one, in the [index](README.md#file-format).
- **Rows:** 1,848 in the 2026-11-19 snapshot.

The sanctions are registered by the sanctioning bodies in the
Banco de Sanções, the system behind the register. The columns are
those of [ceis](ceis.md), plus `VALOR DA MULTA` after
`CATEGORIA DA SANÇÃO`.

## CNEP

One row per sanction.

**Identifies a row:** `CÓDIGO DA SANÇÃO`, unique. A company can have
many sanctions, as a fine and the publication of the decision: 679
documents appear more than once.

The meanings follow the official dictionary; the notes come from the
data.

| Column | Bronze name | Type | Meaning | Notes |
| --- | --- | --- | --- | --- |
| `CADASTRO` | `cadastro` | string | register the sanction belongs to | always `CNEP` |
| `CÓDIGO DA SANÇÃO` | `codigo_da_sancao` | string | sanction id in the Banco de Sanções | 5 to 6 digits |
| `TIPO DE PESSOA` | `tipo_de_pessoa` | string | sanction on a person (`F`) or a company (`J`) | `J` in 98%; empty in 12 rows, foreign entities |
| `CPF OU CNPJ DO SANCIONADO` | `cpf_ou_cnpj_do_sancionado` | string | Receita Federal registration: CPF for a person, CNPJ for a company | not masked, no punctuation; other lengths for foreign entities |
| `NOME DO SANCIONADO` | `nome_do_sancionado` | string | name as the Portal da Transparência shows it | |
| `NOME INFORMADO PELO ÓRGÃO SANCIONADOR` | `nome_informado_pelo_orgao_sancionador` | string | name as the registering body wrote it in the Banco de Sanções, or as published in the DOU | differs from the name above in 8% |
| `RAZÃO SOCIAL - CADASTRO RECEITA` | `razao_social_cadastro_receita` | string | legal name from the Receita Federal CNPJ or CPF registry, looked up by the document | `SEM INFORMACAO` in 12 |
| `NOME FANTASIA - CADASTRO RECEITA` | `nome_fantasia_cadastro_receita` | string | trade name from the same lookup | empty in 35% |
| `NÚMERO DO PROCESSO` | `numero_do_processo` | string | process in which the sanction was applied | free format |
| `CATEGORIA DA SANÇÃO` | `categoria_da_sancao` | string | category of the penalty, among those of the Anti-Corruption Law | 8 values, see below |
| `VALOR DA MULTA` | `valor_da_multa` | decimal(18,2) | fine applied, BRL; the sanction leaves the register once its payment is recorded | 2 decimal places; above zero exactly for the `Multa` rows, `0,00` in the rest |
| `DATA INÍCIO SANÇÃO` | `data_inicio_sancao` | date | start of the penalty; the publication date when no start is stated | from 2016 |
| `DATA FINAL SANÇÃO` | `data_final_sancao` | date | end of the penalty | empty in 98% |
| `DATA PUBLICAÇÃO` | `data_publicacao` | date | publication of the sanction in an official vehicle | empty in 4% |
| `PUBLICAÇÃO` | `publicacao` | string | official vehicle where it was published | with section and page; `Sem Informação` in 4% |
| `DETALHAMENTO DO MEIO DE PUBLICAÇÃO` | `detalhamento_do_meio_de_publicacao` | string | details of the publication | empty in 84% |
| `DATA DO TRÂNSITO EM JULGADO` | `data_do_transito_em_julgado` | date | date the court decision became final (optional) | empty in 68% |
| `ABRAGÊNCIA DA SANÇÃO` | `abragencia_da_sancao` | string | reach of the sanction's effects, set by the registering body | spelled `ABRAGÊNCIA` at the source; `Sem Informação` in 25% |
| `ÓRGÃO SANCIONADOR` | `orgao_sancionador` | string | body that applied the sanction | free text |
| `UF ÓRGÃO SANCIONADOR` | `uf_orgao_sancionador` | string | state of that body | empty in 40% |
| `ESFERA ÓRGÃO SANCIONADOR` | `esfera_orgao_sancionador` | string | its sphere: `FEDERAL`, `ESTADUAL` or `MUNICIPAL` | always filled |
| `FUNDAMENTAÇÃO LEGAL` | `fundamentacao_legal` | string | legal provision behind the sanction | mostly `LEI 12846 - ART. ...` |
| `DATA ORIGEM INFORMAÇÃO` | `data_origem_informacao` | date | date the sanction was registered in the Banco de Sanções | |
| `ORIGEM INFORMAÇÕES` | `origem_informacoes` | string | body that registered the sanction, see below | |
| `OBSERVAÇÕES` | `observacoes` | string | optional free text: origin of the record, extra details, the reach of the sanction | empty in 77% |

`ORIGEM INFORMAÇÕES` is not always the sanctioning body. It can be a
body that registers for others, as a state government's central body
for all its departments.

`CATEGORIA DA SANÇÃO`, by frequency: Multa (56%), Publicação
extraordinária da decisão condenatória (40%), Proibição de receber
incentivos, subsídios, subvenções, doações ou empréstimos, Declaração
de Inidoneidade com prazo determinado, Suspensão/Interdição das
atividades com prazo determinado, Dissolução compulsória da PJ,
Perdimento de bens and Suspensão/Interdição das atividades sem prazo
determinado.

## Known issues

- **Only unpaid fines:** a fine leaves the register once its payment
  is recorded, so the snapshots hold the fines not yet paid. The total
  fined over time cannot come from one snapshot, only from comparing
  snapshots, which are not kept.
- **Fine as a column of every row:** `VALOR DA MULTA` is `0,00`, not
  empty, for the 44% of sanctions that are no fine. Summing it is
  right; averaging it is not.
- **No end date:** `DATA FINAL SANÇÃO` is empty in 98%, as fines and
  publications have no duration.
- **Start date may be the publication date:** when the decision states
  no start, `DATA INÍCIO SANÇÃO` holds the publication date.
- **Sanction after the snapshot date:** one row starts on 2026-11-20,
  a day after the date in the file name. The file is generated the day
  after that date.
- **Personal data:** the CPF of the few sanctioned people comes in
  full. Keep it out of any public output.
- **Documents of foreign entities:** with `TIPO DE PESSOA` empty, the
  document has 7, 9 or 11 digits and is no CPF or CNPJ.
- **Free text where a code would fit:** `ÓRGÃO SANCIONADOR` and
  `ORIGEM INFORMAÇÕES`.
