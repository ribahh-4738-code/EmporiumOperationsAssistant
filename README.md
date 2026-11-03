# Emporium Operations Assistant

Protótipo de agente de atendimento para a **Empório da Música** (loja fictícia de instrumentos em Campo Grande/MS). Persona **Maiara**, interface **CLI** (`./chat.sh`).

**Repositório público:** [github.com/ribahh-4738-code/EmporiumOperationsAssistant](https://github.com/ribahh-4738-code/EmporiumOperationsAssistant)

## Sobre o agente

A Maiara responde com base em contexto injetado a cada turno:

| Fonte | Uso |
|--------|-----|
| **PostgreSQL** (`data/*.csv`) | Catálogo (produtos, preços, estoque), pedidos, promoções |
| **Bloco fixo da loja** | Endereço e contato (**§1.2**) e horários (**§2**) de [`data/políticas_da_loja.pdf`](data/políticas_da_loja.pdf) — injetado sempre; RAG complementa o restante do manual |
| **ChromaDB + PDF** | Políticas: pagamento, trocas, devoluções, prazos |
| **Histórico** | Últimas mensagens em `assistant_chat_message` |

Ela distingue **dados operacionais** (SQL) de **regras** (RAG) e recusa perguntas fora do escopo da loja (módulo `out_of_scope`).

## Início rápido

1. **Pré-requisitos:** Docker, Python 3.11+, Bash.
2. **`./install.sh`** — PostgreSQL, schema, CSVs, persona Maiara, ChromaDB, ingestão do PDF de políticas (passos incrementais; `[skip]` / `[run]`).
3. Edite **`.env`** e defina **`GEMINI_API_KEY`** (chat + embeddings RAG). Se o install rodou antes da chave existir, veja [Scripts após o install](#scripts-após-o-install).
4. **`./chat.sh`** — conversa com a Maiara.

```bash
chmod +x install.sh chat.sh
./install.sh
# editar .env → GEMINI_API_KEY=...
./chat.sh
```

Comandos na sessão: `/sair`, `/exit` ou Ctrl+D; `/cliente <id>` ou `/cliente` (contexto de pedidos — ver Marco 7).

Após `./install.sh`, a migration **006** atualiza o `system_prompt` da Maiara. Instalações antigas também podem rodar:

```bash
.venv/bin/python -m emporium_operations_assistant.assistant.seed_defaults --force-profile
```

Testes (opcional): `.venv/bin/pip install -e ".[dev]"` e `./scripts/test.sh`.

## Decisões técnicas

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| **Abordagem do agente** | Híbrido **RAG + SQL context injection** | Políticas em linguagem natural no PDF → embeddings + busca semântica; catálogo/pedidos tabulares → SQL parametrizado por turno. Sem ReAct/function calling formal: menor complexidade e custo previsível no protótipo. |
| **LLM** | **Google Gemini** (`gemini-3.6-flash` chat, `gemini-embedding-001` RAG) | API estável, bom PT-BR, embeddings no mesmo provedor. |
| **Interface** | **CLI** | Foco no agente; WhatsApp (Meta) ficou fora do escopo após spike. |
| **Persistência** | PostgreSQL (`assistant_chat_message`) | Auditoria e continuidade da conversa por `channel=cli`. |
| **Dados** | CSV seed + truncate no `./install.sh`; PDF versionado | Réplica local do “sistema externo”; políticas indexadas no Chroma. |
| **Catálogo na pergunta** | Keywords + filtro **até R$ X** quando o cliente menciona teto de preço | Atende consultas tipo “violões até R$1000” sem expor SQL ao modelo. |
| **Pedidos** | Nº do pedido, e-mail ou `--customer-id` | Evita ambiguidade de homônimos; protótipo sem OTP. |

## Limitações conhecidas

- Sem autenticação de cliente no CLI (e-mail ou nº do pedido expõe dados — aceitável só em demo).
- Busca de catálogo: top-N por keywords, não é busca full-text avançada nem recomendação ML.
- RAG depende de ingest do PDF e da qualidade do chunk; perguntas vagas podem não retornar trecho.
- Gemini exige `GEMINI_API_KEY` e rede; custo por token (observável em `./logs.sh --pretty`).
- WhatsApp, UI web, function calling nativo e modelo local não implementados.

**Com mais tempo:** autenticação (OTP), tools Gemini para SQL/RAG sob demanda, canal WhatsApp, filtros de catálogo mais ricos, avaliação offline (RAGAS), cache de embeddings.

## Uso de assistentes de IA (workflow)

Este repositório foi desenvolvido com **Cursor** (Agent + planos incrementais):

- Marcos versionados (`v0.1.0` … `v0.9.0`) com commits e tags reais.
- Planos locais em `MDs/` (gitignored) para alinhar escopo antes de codar.
- A IA gerou boilerplate, testes pytest, scripts bash e docs; **revisão humana** em schema, prompts, seed e exemplos de entrega.
- Testes (`./scripts/test.sh`) e smoke manual (`./chat.sh`) antes de release.

Ferramentas como Copilot/Claude poderiam substituir parte do fluxo; o critério foi **decisões documentadas** e código executável, não código gerado sem validação.

## Exemplos de interação (entrega)

Transcripts de referência (cenários do desafio técnico), em [`delivery/examples/`](delivery/examples/):

| Arquivo | Cenário |
|---------|---------|
| [01_violoes_ate_1000.md](delivery/examples/01_violoes_ate_1000.md) | Catálogo + filtro de preço |
| [02_endereco_loja.md](delivery/examples/02_endereco_loja.md) | Endereço e horários |
| [03_preco_takamine_gd20.md](delivery/examples/03_preco_takamine_gd20.md) | Preço de produto |
| [04_devolucao_arrependimento.md](delivery/examples/04_devolucao_arrependimento.md) | Política de devolução (RAG) |
| [05_status_pedido_email.md](delivery/examples/05_status_pedido_email.md) | Status de pedido por e-mail |

Reproduza com `./chat.sh` usando as mesmas perguntas; respostas exatas podem variar levemente com o modelo.

## Stack

| Componente | Uso |
|------------|-----|
| **Python** | Aplicação principal |
| **PostgreSQL** | Catálogo, pedidos, clientes, persona (`assistant_*`) |
| **ChromaDB** | Busca semântica (PDF de políticas da loja) |
| **Gemini** | Chat e embeddings RAG |

## Fora do escopo (por enquanto)

Itens **não** previstos nesta fase do protótipo (tempo / prioridade):

| Item | Notas |
|------|--------|
| **Dashboard** | Alteração ou importação de dados via UI (hoje: CSVs + `./install.sh` / scripts `scripts/db/`) |
| **WhatsApp (Meta Cloud API)** | Canal de atendimento oficial; rollback anterior — retomar só se fizer sentido |
| **Modelo local treinado e/ou quantizado** | LLM on-prem; hoje `LLM_PROVIDER=gemini` com adapter stub local apenas para smoke test |
| **Rotação de API keys** | Chave única em `.env`; sem vault, rotação automática ou multi-key |
| **Busca de pedidos por nome** | Só **nº do pedido** e **e-mail** (e sessão CLI); homônimos ficam fora deste protótipo |
| **Login / OTP em pedidos** | Quem souber e-mail ou nº do pedido vê dados no CLI — não é canal autenticado |

## Marco 8 (v0.8.0) — Testes

O projeto usa **pytest**. As dependências de desenvolvimento **não** entram no `./install.sh` normal — instale uma vez após criar o `.venv`:

```bash
.venv/bin/pip install -e ".[dev]"
```

### Como rodar

| Comando | Quando usar |
|---------|-------------|
| **`./scripts/test.sh`** | Padrão antes de commit: **não** exige Docker, `GEMINI_API_KEY`, Chroma nem Postgres |
| **`./scripts/test.sh --integration`** | Depois do `./install.sh`, com Postgres no ar: smoke de SQL real (pedido #8) |
| **`.venv/bin/pytest -q`** | Equivalente ao script (exclui `@pytest.mark.integration`) |
| **`.venv/bin/pytest -q -m integration`** | Só testes marcados como integração |

**CI (GitHub Actions):** o workflow está em [`.github/workflows/tests.yml`](.github/workflows/tests.yml) (pytest igual ao `./scripts/test.sh`). Se o `git push` falhar por falta de scope `workflow` no token OAuth, rode `gh auth refresh -s workflow` e envie só esse arquivo, ou crie o workflow pela UI do GitHub.

### O que cada camada testa

**Unitários** (`tests/unit/`) — funções puras ou com mocks; rápidos e determinísticos:

| Arquivo | Foco |
|---------|------|
| `test_chunking.py` | Divisão de texto para RAG (`chunk_text`) |
| `test_order_lookup.py` | Extração de **nº do pedido** e **e-mail** (frases do Marco 7) |
| `test_catalog_search.py` | Keywords de catálogo e filtro **até R$ X** |
| `test_llm_history.py` | Regras Gemini: turnos `user`/`model` alternados |
| `test_order_context_format.py` | Texto do bloco de pedidos (SQL mockado) |
| `test_observability.py` | JSONL em path temporário + contador diário de tokens |
| `test_seed_validate.py` | Cabeçalhos de `data/*.csv` batem com `db/seed/manifest.json` |

**Integração leve** (`tests/integration/test_rag_ingest_light.py`) — pipeline de ingest **sem** API Gemini e **sem** container Chroma:

- `chromadb.EphemeralClient` (memória)
- PDF e embeddings **mockados**; fixture de texto em `tests/fixtures/rag/sample_policy.txt`
- Valida indexação, hash idempotente (segundo ingest sem `--force` = skip) e `search_policy_chunks`

**Integração Postgres** (`tests/integration/test_postgres_orders.py`) — marcada com `@pytest.mark.integration`:

- Conecta com credenciais do `.env` (`POSTGRES_*`)
- Se o banco não responder, o teste é **skipped** (não falha o CI nem quem não subiu Docker)

### O que os testes não cobrem (por enquanto)

- Chat end-to-end com Gemini (custo/API)
- Ingest do PDF real `data/políticas_da_loja.pdf` em CI
- Chroma HTTP na porta 8001

### Layout

```
tests/
├── conftest.py           # paths temporários (.run / JSONL)
├── unit/
├── integration/
└── fixtures/rag/
```

## Marco 7 (v0.7.0) — Consulta de pedidos

A Maiara inclui **pedidos reais do PostgreSQL** no contexto quando você informa:

| Forma | Exemplo |
|--------|---------|
| **Número do pedido** na mensagem | “Quero saber do **pedido 8**” |
| **E-mail cadastrado** na mensagem | “Gostaria de saber o status do meu pedido, meu e-mail é **rafael.pereira@jmail.com**” |
| **Sessão CLI** (opcional) | `./chat.sh --customer-id 2` ou `CHAT_CUSTOMER_ID` no `.env`; na sessão: `/cliente 2` ou `/cliente` para limpar |

**Não há busca por nome completo** (evita ambiguidade). O nome do cliente pode aparecer no bloco depois que o pedido ou e-mail foi identificado.

```bash
./chat.sh
./chat.sh --customer-id 2
```

### Exemplos de perguntas (copie no chat)

Use dados do seed em [`data/customers.csv`](data/customers.csv) e [`data/orders.csv`](data/orders.csv).

**Pedidos (e-mail ou número do pedido)**

- Gostaria de saber o status do meu pedido, meu e-mail é **rafael.pereira@jmail.com**
- Quero saber do **pedido 8** — qual o rastreio?
- Meu e-mail é **lucas.mendes@jmail.com**, quais são meus pedidos?

**Pedidos (sessão CLI)** — após `./chat.sh --customer-id 2`:

- Qual o status do meu pedido?
- Onde está meu rastreio?

**Catálogo**

- Quais opções de **violões** disponíveis custando **até R$1000**?
- Vocês têm **violão Yamaha** disponível?
- Quanto custa o **Takamine GD20**?

**Políticas da loja (RAG no PDF)**

- Quais **formas de pagamento** vocês aceitam?
- Como funciona o **parcelamento**?

Limites: `ORDER_CONTEXT_LIMIT` (pedidos listados por cliente), `ORDER_DETAIL_MAX_ITEMS` (itens por pedido) — [`.env.example`](.env.example).

## Marco 6 (v0.6.0) — Observabilidade + catálogo inteligente

- **[`./logs.sh`](logs.sh)** — em outro terminal, acompanha SQL/RAG/embeddings/Gemini (`--pretty` para leitura humana); arquivo padrão `.run/assistant.jsonl`
- **[`./scripts/status.sh`](scripts/status.sh)** — healthcheck Postgres + Chroma + coleção `store_policies` + contagem de chunks
- **Catálogo no prompt** — top-N produtos por palavras-chave da pergunta (SQL), além do resumo agregado e do RAG
- **Tokens Gemini** — por turno no log; `GEMINI_DAILY_TOKEN_BUDGET` gera **aviso só no log** (chat continua)

```bash
./scripts/status.sh          # stack ok?
./chat.sh                    # terminal 1
./logs.sh --pretty           # terminal 2
```

## Marco 5 (v0.5.0) — ChromaDB + políticas da loja

- ChromaDB + **ChromaDB Admin** (passo 11 do install)
- RAG sobre [`data/políticas_da_loja.pdf`](data/políticas_da_loja.pdf) (parcelamento e demais políticas)
- Se alterar o PDF: `./scripts/chroma/ingest_rag.sh` (ou `--force`)

## Marco 4 (v0.4.0) — Chat CLI

- [`./chat.sh`](chat.sh) / `emporium-chat` — histórico PostgreSQL, resumo de catálogo, Gemini

## Chat (`./chat.sh`)

O assistente combina: `system_prompt` da Maiara, prompts modulares, **dados da loja**, resumo PostgreSQL, **produtos relacionados (SQL, com filtro de preço quando aplicável)**, **pedidos (nº do pedido, e-mail ou sessão CLI)**, **trechos do PDF (ChromaDB)** e últimas `CHAT_HISTORY_LIMIT` mensagens (`channel=cli`).

Manifesto RAG: [`db/seed/rag_manifest.json`](db/seed/rag_manifest.json).

### ChromaDB (API + Admin + RAG)

| Serviço | URL padrão | Uso |
|---------|------------|-----|
| Chroma API | `http://localhost:8001` | Coleção `store_policies` |
| **ChromaDB Admin** | `http://127.0.0.1:3001` | UI ([flanker/chromadb-admin](https://github.com/flanker/chromadb-admin)) |

No Admin, URL do servidor: `http://host.docker.internal:8001` (ajuste `CHROMA_PORT` se necessário). Coleção: **`store_policies`**.

**Atualizar o PDF:** se alterar o PDF: `./scripts/chroma/ingest_rag.sh` (ou `--force`).

Na primeira execução do chat, se a coleção não existir, o `./chat.sh` sobe o Chroma e tenta **indexar o PDF** automaticamente.

**Versões:** client Python `chromadb` 1.5.x exige imagem **`chromadb/chroma:1.5.9`**. Embeddings: **`gemini-embedding-001`**. Se ingest falhar após upgrade: recrie o container com [`ensure_chroma_container.sh`](scripts/chroma/ensure_chroma_container.sh) e [`ingest_rag.sh --force`](scripts/chroma/ingest_rag.sh). Ver também [CHANGELOG](CHANGELOG.md) `[0.5.0]`.

## Configuração

- **`.env`** — copie de [`.env.example`](.env.example); chaves sensíveis só localmente.
- Persona e prompts modulares — **PostgreSQL** (`assistant_*`), seed no install (passo 10).

## Instalação (`./install.sh`)

```bash
./install.sh --dry-run   # preview
./install.sh
```

O instalador:

1. `.env` a partir de `.env.example` (se ausente) + sync de chaves novas
2. Container **`emporium_ops_postgres`** (porta **5435**)
3. Banco `emporium_operation`, `db/schema.sql`, migrations pendentes
4. `.venv` + dependências Python
5. Import CSV (`data/*.csv`) — **truncate** das tabelas operacionais a cada run
6. Verificação de contagens ([`db/seed/manifest.json`](db/seed/manifest.json))
7. Seed Maiara (`assistant_profile` / `assistant_prompt`) — **não** apaga `assistant_chat_message`
8. Containers **`emporium_ops_chroma`** (8001) e **`emporium_ops_chroma_admin`** (3001)
9. Ingest RAG dos PDFs do manifesto ( **pula** indexação se `GEMINI_API_KEY` vazia)

Conexões: PostgreSQL `localhost:5435`, Chroma `8001`, Admin `http://127.0.0.1:3001`.

### Scripts após o install

| Script | Quando usar | Por quê |
|--------|-------------|---------|
| **[`./chat.sh`](chat.sh)** | Uso diário | Chat com a Maiara; garante container Chroma; grava log em `.run/` |
| **[`./logs.sh`](logs.sh)** | Debug em paralelo | `tail -f` do JSONL (SQL, RAG, tokens) |
| **[`./scripts/status.sh`](scripts/status.sh)** | Verificar stack | Postgres, Chroma, chunks indexados |
| **[`./scripts/test.sh`](scripts/test.sh)** | Regressão rápida | pytest (dev deps); `--integration` com Postgres local |
| [`scripts/chroma/ingest_rag.sh`](scripts/chroma/ingest_rag.sh) | PDF de políticas alterado ou ingest falhou no install | Reindexa `store_policies` no Chroma |
| [`scripts/chroma/ingest_rag.sh --force`](scripts/chroma/ingest_rag.sh) | Mesmo PDF, quer rebuild completo | Ignora hash e recria a coleção |
| [`scripts/chroma/ensure_chroma_container.sh`](scripts/chroma/ensure_chroma_container.sh) | Docker reiniciado / Chroma parado | Sobe API Chroma 1.5.9 |
| [`scripts/chroma/ensure_chroma_admin_container.sh`](scripts/chroma/ensure_chroma_admin_container.sh) | Admin UI offline | Sobe UI na porta 3001 |
| [`scripts/db/verify_seed.sh`](scripts/db/verify_seed.sh) | Conferir CSV importado | Compara linhas com o manifest |
| [`./install.sh`](install.sh) de novo | CSVs ou schema mudaram | Reaplica migrations, reimporta CSVs, RAG idempotente |

Se após o install **não** havia `GEMINI_API_KEY`: defina a chave no `.env` e rode **`./scripts/chroma/ingest_rag.sh`** (ou apenas **`./chat.sh`**, que tenta indexar na abertura).

### Dados de seed e truncate

CSVs em [`data/`](data/) = export do sistema externo; cada `./install.sh` **substitui** categorias, clientes, produtos, pedidos e promoções. Tabelas `assistant_*` e histórico de chat **não** são truncadas.

### Conferir seed

```bash
./scripts/db/verify_seed.sh
```

### Assistente (PostgreSQL + LLM)

| Tabela | Uso |
|--------|-----|
| `assistant_profile` | Persona (`system_prompt`, …) |
| `assistant_prompt` | Prompts por `module_key` |
| `assistant_chat_message` | Auditoria (`user` / `model`, `channel`) |

Variáveis principais: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`, `CHROMA_*`, `RAG_*`, `ASSISTANT_LOG_PATH`, `GEMINI_DAILY_TOKEN_BUDGET`, `CATALOG_SEARCH_LIMIT`, `CHAT_CUSTOMER_ID`, `ORDER_CONTEXT_LIMIT` — ver [`.env.example`](.env.example).

Teste Gemini (opcional):

```bash
.venv/bin/python -m emporium_operations_assistant.llm.adapters.gemini
```

## Setup manual (sem Docker no Postgres)

Ajuste `.env` e execute em ordem: `scripts/db/create_database.sh`, `apply_schema.sh`, `apply_migrations.sh`, `import_seed.sh`, `verify_seed.sh`, `seed_assistant.sh`, depois scripts em `scripts/chroma/`.

## Estrutura do repositório

```
EmporiumOperationsAssistant/
├── install.sh
├── chat.sh
├── logs.sh
├── delivery/examples/      # transcripts de entrega (desafio)
├── tests/                  # pytest (unit + integration leve)
├── data/
├── src/emporium_operations_assistant/
│   ├── assistant/  cli/  llm/  observability/  rag/  seed/
└── scripts/
    ├── test.sh
    ├── status.sh
    ├── chat.sh             # redireciona para ./chat.sh
    ├── chroma/
    └── db/
```

## Dados de seed (`data/`)

| Arquivo | Descrição |
|---------|-----------|
| `categories.csv` … `promotions.csv` | Operacional (import no install) |
| `políticas_da_loja.pdf` | Políticas / parcelamento (RAG) |

Planos locais: pasta `MDs/` (gitignored).

## Histórico de versões

Evolução por marcos (detalhes no [CHANGELOG.md](CHANGELOG.md)): v0.1 schema → v0.2 CSV → v0.3–4 chat Gemini → v0.5 RAG → v0.6 observabilidade → v0.7 pedidos → v0.8 pytest → **v0.9 entrega Artefact**.
