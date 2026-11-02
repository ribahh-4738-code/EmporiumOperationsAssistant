# Emporium Operations Assistant

Assistente conversacional para operações de um emporium de instrumentos musicais. O sistema utiliza a persona **Maiara**, com **CLI** para testes; WhatsApp fica fora do escopo deste protótipo.

## Stack planejada

| Componente | Uso |
|------------|-----|
| **Python** | Aplicação principal e integrações |
| **PostgreSQL** | Banco relacional (catálogo, pedidos, clientes, configurações) |
| **ChromaDB** | Busca semântica sobre conteúdo do emporium |
| **WhatsApp** | Canal de atendimento (marco futuro, se necessário) |

## Configuração

- Variáveis de ambiente sensíveis e de infraestrutura ficam no arquivo **`.env`** (use [`.env.example`](.env.example) como modelo).
- Textos da persona e prompts modulares ficam no **PostgreSQL** (`assistant_*`). No **`.env`**: provider/modelo LLM, nome exibido da atendente (`ASSISTANT_DISPLAY_NAME`), chaves de API.

## Marco 5 (v0.5.0) — ChromaDB + políticas da loja

**Entregue neste marco:**

- ChromaDB em Docker (passos 11–12 do [`./install.sh`](install.sh), sem setup manual)
- **ChromaDB Admin** (UI web no passo 11) para inspecionar coleções e documentos indexados
- Ingestão do PDF [`data/políticas_da_loja.pdf`](data/políticas_da_loja.pdf) (parcelamento e demais políticas)
- RAG na CLI: trechos relevantes entram no contexto da Maiara a cada pergunta (embeddings Gemini)
- Se alterar o PDF: `./scripts/chroma/ingest_rag.sh` (ou `--force`).

**Próximo marco (previsto):** novos documentos no manifesto RAG, refinamentos de persona.

## Marco 4 (v0.4.0) — Chat CLI

- CLI interativa (`emporium-chat` / [`scripts/chat.sh`](scripts/chat.sh))
- `ChatService`: histórico no PostgreSQL, Gemini, resumo do catálogo em contexto

## Chat na linha de comando

1. Conclua o [`./install.sh`](install.sh) (PostgreSQL + Chroma + ingestão do PDF de políticas).
2. Edite `.env` e defina `GEMINI_API_KEY=...` (usada no chat e nos embeddings RAG).
3. Inicie o chat:

```bash
./scripts/chat.sh
# ou
.venv/bin/emporium-chat
```

Comandos na sessão: `/sair`, `/exit` ou Ctrl+D.

Cada mensagem é gravada em `assistant_chat_message` com `channel=cli`. O assistente usa o `system_prompt` da Maiara no banco, prompts modulares, resumo de produtos/pedidos do PostgreSQL, **trechos semânticos do PDF de políticas (ChromaDB)** e as últimas `CHAT_HISTORY_LIMIT` mensagens (padrão 20).

Manifesto de arquivos: [`db/seed/rag_manifest.json`](db/seed/rag_manifest.json).

### ChromaDB (API + Admin + RAG)

| Serviço | URL padrão | Uso |
|---------|------------|-----|
| Chroma API | `http://localhost:8001` | Embeddings e coleção `store_policies` (app + ingest) |
| **ChromaDB Admin** | `http://127.0.0.1:3001` | UI não oficial ([flanker/chromadb-admin](https://github.com/flanker/chromadb-admin)) — sobe no passo 11 do install |

Na primeira tela do Admin, informe a URL do servidor Chroma:

`http://host.docker.internal:8001`

(ajuste a porta se `CHROMA_PORT` no `.env` for diferente). Tenant/database padrão costumam ser `default_tenant` / `default_database`. A coleção indexada pelo projeto é **`store_policies`**.

**Atualizar o PDF de políticas:** se alterar o PDF: `./scripts/chroma/ingest_rag.sh` (ou `--force`).

Na primeira execução do chat, se a coleção `store_policies` ainda não existir (por exemplo, ingest pulada no install sem `GEMINI_API_KEY`), o `./scripts/chat.sh` sobe o Chroma e **indexa o PDF automaticamente** antes da conversa.

**Versões:** o pacote Python `chromadb` (1.5.x) exige a imagem Docker **`chromadb/chroma:1.5.9`** (não use `0.6.x`). O script `ensure_chroma_container.sh` recria o container se a imagem estiver desatualizada. Embeddings: `GEMINI_EMBEDDING_MODEL=gemini-embedding-001` (não `text-embedding-004`).

Se ingest falhar após upgrade de imagem: `docker stop emporium_ops_chroma && docker rm emporium_ops_chroma`, depois `./scripts/chroma/ensure_chroma_container.sh` e `./scripts/chroma/ingest_rag.sh --force`.

```bash
./scripts/chroma/ingest_rag.sh
./scripts/chroma/ingest_rag.sh --force   # reindex mesmo sem mudança de hash
```

## Pré-requisitos

- **Docker** (PostgreSQL do projeto roda em container; não é necessário informar senha manualmente)
- **Python 3.11+**
- Bash

## Instalação (`./install.sh`)

O script na raiz instala de forma **incremental** (novos passos serão adicionados nos próximos marcos).

**Ver o que será executado (sem alterar nada):**

```bash
chmod +x install.sh
./install.sh --dry-run
```

**Instalar (container PostgreSQL + schema):**

```bash
./install.sh
```

O instalador:

1. Cria `.env` a partir de `.env.example` se ainda não existir (credenciais de **desenvolvimento local** já preenchidas)
2. Sobe o container `emporium_ops_postgres` (imagem `postgres:16-alpine`, volume persistente)
3. Garante o banco `emporium_operation`, aplica `db/schema.sql` (somente DDL) e migrations pendentes
4. Cria `.venv`, instala dependências e **importa os CSVs** (truncate + load)
5. Verifica contagens de linhas contra [`db/seed/manifest.json`](db/seed/manifest.json)
6. Garante profile/prompts do assistente (passo 10; **não** apaga `assistant_chat_message`)
7. Sobe `emporium_ops_chroma` (API, porta **8001**) e `emporium_ops_chroma_admin` (UI, porta **3001**)
8. Indexa PDFs listados em [`db/seed/rag_manifest.json`](db/seed/rag_manifest.json) no Chroma (reindex só se o arquivo mudar; se alterar o PDF, rode `./scripts/chroma/ingest_rag.sh` ou `--force`)

Passos já satisfeitos aparecem como `[skip]`; passos executados como `[run]`.

Conexões padrão após o install: PostgreSQL `localhost:5435`, Chroma `localhost:8001`, Admin `http://127.0.0.1:3001` (ver `.env`).

### Dados de seed e truncate

As tabelas alimentadas pelos CSVs (`categories`, `customers`, `products`, `orders`, `order_items`, `promotions`) são **sempre truncadas** antes de cada import no `./install.sh`. Os arquivos em [`data/`](data/) representam uma **exportação de outro sistema** (fonte operacional); o PostgreSQL local é uma réplica para consulta do assistente, não a fonte da verdade. Por isso cada install **substitui** o conteúdo dessas tabelas — não há merge incremental. Tabelas `assistant_*` **não** entram nesse truncate. O histórico em `assistant_chat_message` é preservado entre installs.

O arquivo [`db/schema.sql`](db/schema.sql) **não contém dados** — apenas DDL. Dados entram somente via import dos CSVs.

### Conferir dados após o install

```bash
./scripts/db/verify_seed.sh
# ou
.venv/bin/python -m emporium_operations_assistant.seed.verify
```

Se a estrutura de um CSV mudar, atualize `manifest.json`, `schema.sql` e adicione um arquivo em `db/migrations/` (veja [`db/migrations/README.md`](db/migrations/README.md)).

### Assistente (PostgreSQL + LLM)

| Tabela | Uso |
|--------|-----|
| `assistant_profile` | Persona (`system_prompt`, timezone, `profile_name`) |
| `assistant_prompt` | Prompts por `module_key` (ex. `reformulate_request`) |
| `assistant_chat_message` | Auditoria (`role`: `user` ou `model`, `message_text`, `model`, `channel`) |

Variáveis no `.env` (ver [`.env.example`](.env.example)):

- `ASSISTANT_DISPLAY_NAME`, `ASSISTANT_PROFILE_NAME`
- `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`
- Chroma: `CHROMA_HOST`, `CHROMA_PORT`, `CHROMA_COLLECTION`, `RAG_TOP_K`, `CHROMA_ADMIN_PORT`

Teste opcional do adapter (requer chave):

```bash
export GEMINI_API_KEY=...
.venv/bin/python -m emporium_operations_assistant.llm.adapters.gemini
```

Smoke test sem API:

```bash
DRY_RUN=1 .venv/bin/python -m emporium_operations_assistant.llm.adapters.gemini
```

Planos de marco locais (não versionados): pasta `MDs/` (ver `.gitignore`).

## Setup manual (opcional, sem Docker)

Se preferir PostgreSQL no host, ajuste `.env` (por exemplo porta `5432`) e use:

```bash
./scripts/db/create_database.sh
./scripts/db/apply_schema.sh
./scripts/db/apply_migrations.sh
./scripts/db/import_seed.sh
./scripts/db/verify_seed.sh
./scripts/db/seed_assistant.sh
```

## Estrutura do repositório

```
EmporiumOperationsAssistant/
├── CHANGELOG.md
├── README.md
├── install.sh
├── pyproject.toml
├── data/                 # CSVs (export do sistema externo)
├── db/
│   ├── schema.sql        # DDL baseline (sem INSERT)
│   ├── seed/manifest.json
│   └── migrations/
├── src/emporium_operations_assistant/
│   ├── config.py
│   ├── assistant/        # chat, repository, catalog context
│   ├── cli/              # emporium-chat
│   ├── llm/              # adapters (gemini, local stub)
│   ├── rag/              # Chroma ingest + retrieval
│   └── seed/             # CSV validate, import, verify
└── scripts/
    ├── chat.sh               # inicia CLI
    ├── chroma/               # container + ingest RAG
    ├── lib/
    │   ├── env.sh
    │   └── psql.sh
    └── db/
        ├── apply_migrations.sh
        ├── apply_schema.sh
        ├── create_database.sh
        ├── ensure_postgres_container.sh
        ├── ensure_venv.sh
        ├── import_seed.sh
        ├── seed_assistant.sh
        └── verify_seed.sh
```

## Dados de seed (`data/`)

| Arquivo | Descrição |
|---------|-----------|
| `categories.csv` | Categorias de produtos |
| `customers.csv` | Clientes |
| `products.csv` | Produtos (campo `specs` em JSON) |
| `orders.csv` | Pedidos |
| `order_items.csv` | Itens por pedido |
| `promotions.csv` | Promoções por produto |

## Repositório

[github.com/ribahh-4738-code/EmporiumOperationsAssistant](https://github.com/ribahh-4738-code/EmporiumOperationsAssistant)
