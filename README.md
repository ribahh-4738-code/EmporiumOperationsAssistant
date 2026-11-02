# Emporium Operations Assistant

Assistente conversacional para operações de um emporium de instrumentos musicais. O sistema utiliza a persona **Maiara**, com **CLI** para testes e, em marco futuro, **WhatsApp**.

## Stack planejada

| Componente | Uso |
|------------|-----|
| **Python** | Aplicação principal e integrações |
| **PostgreSQL** | Banco relacional (catálogo, pedidos, clientes, configurações) |
| **ChromaDB** | Busca semântica sobre conteúdo do emporium |
| **WhatsApp** | Canal de atendimento (configuração posterior) |

## Configuração

- Variáveis de ambiente sensíveis e de infraestrutura ficam no arquivo **`.env`** (use [`.env.example`](.env.example) como modelo).
- Textos da persona e prompts modulares ficam no **PostgreSQL** (`assistant_*`). No **`.env`**: provider/modelo LLM, nome exibido da atendente (`ASSISTANT_DISPLAY_NAME`), chaves de API.

## Marco 4 (v0.4.0) — Chat CLI

**Entregue neste marco:**

- CLI interativa (`emporium-chat` / [`scripts/chat.sh`](scripts/chat.sh))
- `ChatService`: histórico no PostgreSQL, Gemini, resumo do catálogo em contexto
- Carregamento automático do `.env` ao iniciar o chat

**Próximo marco (previsto):** ChromaDB (busca semântica), WhatsApp.

## Chat na linha de comando

1. Conclua o [`./install.sh`](install.sh) (banco + persona Maiara).
2. Edite `.env` e defina `GEMINI_API_KEY=...` (e ajuste `GEMINI_MODEL` se quiser).
3. Inicie o chat:

```bash
./scripts/chat.sh
# ou
.venv/bin/emporium-chat
```

Comandos na sessão: `/sair`, `/exit` ou Ctrl+D.

Cada mensagem é gravada em `assistant_chat_message` com `channel=cli`. O assistente usa o `system_prompt` da Maiara no banco, prompts modulares, resumo de produtos/pedidos do PostgreSQL e as últimas `CHAT_HISTORY_LIMIT` mensagens (padrão 20).

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

Passos já satisfeitos aparecem como `[skip]`; passos executados como `[run]`.

Conexão padrão após o install: `localhost:5435`, usuário/senha/banco conforme `.env`.

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
- `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, `GEMINI_MODEL`

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
│   └── seed/             # CSV validate, import, verify
└── scripts/
    ├── chat.sh               # inicia CLI
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
