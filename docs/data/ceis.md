# ceis

Cadastro de Empresas Inidôneas e Suspensas: people and companies
barred from bidding or contracting with the government, by any
federal, state or municipal body. Source:
<https://portaldatransparencia.gov.br/download-de-dados/ceis>.
Official dictionary:
<https://portaldatransparencia.gov.br/dicionario-de-dados/ceis>.

- **Cadence:** a daily snapshot, `YYYYMMDD_CEIS.zip`, of the whole
  register. Only the latest one is kept, so a sanction that leaves the
  register leaves the data.
- **Files:** `YYYYMMDD_CEIS.csv`.
- **Format:** the common one, in the [index](README.md#file-format).
- **Rows:** 23,639 in the 2026-11-19 snapshot.

The sanctions are registered by the sanctioning bodies in the
Banco de Sanções, the system behind the register. [cnep](cnep.md) has
the same columns plus `VALOR DA MULTA`.

## CEIS

One row per sanction.

**Identifies a row:** `CÓDIGO DA SANÇÃO`, unique. A person or company
can have many sanctions: 3,364 documents appear more than once.

The meanings follow the official dictionary; the notes come from the
data.

| Column | Type | Meaning | Notes |
| --- | --- | --- | --- |
| `CADASTRO` | string | register the sanction belongs to | always `CEIS` |
| `CÓDIGO DA SANÇÃO` | string | sanction id in the Banco de Sanções | 5 to 6 digits |
| `TIPO DE PESSOA` | string | sanction on a person (`F`) or a company (`J`) | empty in 11 rows, foreign entities |
| `CPF OU CNPJ DO SANCIONADO` | string | Receita Federal registration: CPF for a person, CNPJ for a company | not masked, no punctuation; other lengths for foreign entities |
| `NOME DO SANCIONADO` | string | name as the Portal da Transparência shows it | |
| `NOME INFORMADO PELO ÓRGÃO SANCIONADOR` | string | name as the registering body wrote it in the Banco de Sanções, or as published in the DOU | differs from the name above in 20% |
| `RAZÃO SOCIAL - CADASTRO RECEITA` | string | legal name from the Receita Federal CNPJ or CPF registry, looked up by the document | never filled for a person; `SEM INFORMACAO` in 11 |
| `NOME FANTASIA - CADASTRO RECEITA` | string | trade name from the same lookup | empty in 56% |
| `NÚMERO DO PROCESSO` | string | process in which the sanction was applied | free format |
| `CATEGORIA DA SANÇÃO` | string | category of the penalty that restricts bidding or contracting | 10 values, see below |
| `DATA INÍCIO SANÇÃO` | date | start of the penalty; the publication date when no start is stated | from 2003 |
| `DATA FINAL SANÇÃO` | date | end of the penalty | empty in 9%; `31/12/2099` in 15; never before the start; a minimum for some sanctions, see [known issues](#known-issues) |
| `DATA PUBLICAÇÃO` | date | publication of the sanction in an official vehicle | empty in 67% |
| `PUBLICAÇÃO` | string | official vehicle where it was published | with section and page; `Sem Informação` in 68% |
| `DETALHAMENTO DO MEIO DE PUBLICAÇÃO` | string | details of the publication | empty in 95% |
| `DATA DO TRÂNSITO EM JULGADO` | date | date the court decision became final (optional) | empty in 49% |
| `ABRAGÊNCIA DA SANÇÃO` | string | reach of the sanction's effects, set by the registering body | spelled `ABRAGÊNCIA` at the source; `Sem Informação` in 43% |
| `ÓRGÃO SANCIONADOR` | string | body that applied the sanction | free text, up to 243 chars |
| `UF ÓRGÃO SANCIONADOR` | string | state of that body | empty in 4% |
| `ESFERA ÓRGÃO SANCIONADOR` | string | its sphere: `FEDERAL`, `ESTADUAL` or `MUNICIPAL` | empty in 143 rows |
| `FUNDAMENTAÇÃO LEGAL` | string | legal provision behind the sanction | as `LEI 14133 - ART. 156, III - ...` |
| `DATA ORIGEM INFORMAÇÃO` | date | date the sanction was registered in the Banco de Sanções | |
| `ORIGEM INFORMAÇÕES` | string | body that registered the sanction, see below | |
| `OBSERVAÇÕES` | string | optional free text: origin of the record, extra details, the reach of the sanction | empty in 56%; at most 2,048 chars |

`ORIGEM INFORMAÇÕES` is not always the sanctioning body. It can be a
body that registers for others: a state government's central body for
all its departments, the CNJ for the sanctions of every court in
administrative improbity suits, or the Ministério da Fazenda for the
sanctions registered through SICAF.

`CATEGORIA DA SANÇÃO`, by frequency: Impedimento/proibição de
contratar com prazo determinado (76%), Suspensão, Declaração de
Inidoneidade sem prazo determinado, Declaração de Inidoneidade com
prazo determinado, Impedimento/proibição de contratar sem prazo
determinado, Demissão, Suspensão/Interdição das atividades sem prazo
determinado, Suspensão/Interdição das atividades com prazo determinado,
Multa and Advertência.

`ABRAGÊNCIA DA SANÇÃO`: Sem Informação, Em todos os Poderes da Esfera
do órgão sancionador, No órgão sancionador, Todas as Esferas em todos
os Poderes, Na Esfera e no Poder do órgão sancionador and Em outro
órgão.

## Known issues

- **Sanctions past their end date still listed:** 563 rows have a
  `DATA FINAL SANÇÃO` before the snapshot date.
  - 335 are declarations of unfitness under Lei 8.666/93, art. 87, IV.
    For these, the official dictionary says the end date is a minimum:
    the sanction stays until it is made inactive in the Banco de
    Sanções, by rehabilitation or another reason. They are in force.
  - The other 228, impediments and suspensions, have no such rule.
  Whether a sanction is in force cannot come from the dates alone.
- **Open-ended sanctions:** an empty `DATA FINAL SANÇÃO` or a date in
  2099 (16 rows) means no end date.
- **Start date may be the publication date:** when the decision states
  no start, `DATA INÍCIO SANÇÃO` holds the publication date.
- **Personal data:** the CPF of sanctioned people comes in full. Keep
  it out of any public output.
- **Documents of foreign entities:** with `TIPO DE PESSOA` empty, the
  document has 7, 9, 11 or 14 digits and is no CPF or CNPJ.
- **Mostly empty columns:** `DATA PUBLICAÇÃO`, `PUBLICAÇÃO`,
  `DETALHAMENTO DO MEIO DE PUBLICAÇÃO` and `ABRAGÊNCIA DA SANÇÃO`.
- **`OBSERVAÇÕES` cut at 2,048 characters.**
- **Free text where a code would fit:** `ÓRGÃO SANCIONADOR` and
  `ORIGEM INFORMAÇÕES` are typed names, with variations, and one
  `ÓRGÃO SANCIONADOR` is a CNPJ.
- **Mixed case:** some upper-case names have lower-case accented
  letters, as `ROGéLIO`.
