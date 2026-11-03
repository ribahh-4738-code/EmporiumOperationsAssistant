# Emporium Operations Assistant

Assistente conversacional para operações de um emporium de instrumentos musicais. O sistema utiliza a persona **Maiara**, com **CLI** para testes.

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

- Vocês têm **violão Yamaha** disponível?
- Qual o preço de uma **bateria**?

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

O assistente combina: `system_prompt` da Maiara, prompts modulares, resumo PostgreSQL, **produtos relacionados (SQL)**, **pedidos (nº do pedido, e-mail ou sessão CLI)**, **trechos do PDF (ChromaDB)** e últimas `CHAT_HISTORY_LIMIT` mensagens (`channel=cli`).

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
├── data/
├── src/emporium_operations_assistant/
│   ├── assistant/  cli/  llm/  observability/  rag/  seed/
└── scripts/
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

## Repositório

[github.com/ribahh-4738-code/EmporiumOperationsAssistant](https://github.com/ribahh-4738-code/EmporiumOperationsAssistant)
