# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [0.8.0] - 2026-11-03

### Adicionado

- **pytest** — extra `dev` em [`pyproject.toml`](pyproject.toml), pasta [`tests/`](tests/)
- [`scripts/test.sh`](scripts/test.sh) — default sem Postgres; `--integration` para smoke de pedidos
- Integração leve RAG: ingest + retrieval com `EphemeralClient` e `embed_texts` mockado
- GitHub Actions [`.github/workflows/tests.yml`](.github/workflows/tests.yml)
- README: instruções detalhadas de pytest (camadas, comandos, limites)

## [0.7.0] - 2026-11-03

### Adicionado

- Contexto de **pedidos reais** no prompt ([`order_context.py`](src/emporium_operations_assistant/assistant/order_context.py)): consulta por **número do pedido** ou **e-mail cadastrado** na mensagem
- Sessão CLI opcional: `./chat.sh --customer-id N`, `CHAT_CUSTOMER_ID`, comandos `/cliente <id>` e `/cliente` (limpar)
- Variáveis `ORDER_CONTEXT_LIMIT`, `ORDER_DETAIL_MAX_ITEMS`

### Alterado

- README: consulta de pedidos (sem busca por nome), exemplos de perguntas (pedidos, catálogo, políticas); protótipo sem login documentado
- Eventos `sql` de pedidos visíveis em [`logs.sh --pretty`](logs.sh)

## [0.6.0] - 2026-11-03

### Adicionado

- [`logs.sh`](logs.sh) — JSONL estruturado (SQL catálogo, RAG, embeddings, tokens Gemini); modo `--pretty`
- [`scripts/status.sh`](scripts/status.sh) — healthcheck Postgres, Chroma, coleção `store_policies`, chunk count
- Módulo `observability/` (eventos, teto diário de tokens com aviso só no log, contador em `.run/`)
- Busca de produtos por keywords da pergunta ([`catalog_search.py`](src/emporium_operations_assistant/assistant/catalog_search.py))
- Uso Gemini em `assistant_chat_message.metadata` quando disponível

### Alterado

- [`build_catalog_context`](src/emporium_operations_assistant/assistant/catalog_context.py) recebe `user_query` para top-N produtos (`CATALOG_SEARCH_LIMIT`)
- [`./chat.sh`](chat.sh) define `ASSISTANT_LOG_PATH` e cria `.run/`
- README: Marco 6, rotação de API keys em “fora do escopo”

## [0.5.0] - 2026-11-02

### Adicionado

- ChromaDB via Docker (`scripts/chroma/ensure_chroma_container.sh`, passos 11–12 do [`install.sh`](install.sh))
- **ChromaDB Admin** UI no install (`emporium_ops_chroma_admin`, porta 3001; imagem `fengzhichao/chromadb-admin`)
- RAG: PDF [`data/políticas_da_loja.pdf`](data/políticas_da_loja.pdf), manifesto [`db/seed/rag_manifest.json`](db/seed/rag_manifest.json)
- Contexto de políticas no `ChatService` (busca semântica por pergunta; embeddings Gemini)
- Bootstrap RAG no chat (`ensure_policy_index`) e `scripts/chroma/ingest_rag.sh`
- Dependências `chromadb` (~1.5.x), `pypdf`; variáveis `CHROMA_*`, `RAG_*`, `GEMINI_EMBEDDING_MODEL` em `.env.example`

### Corrigido

- **`KeyError('_type')` na ingestão RAG:** client Python `chromadb` 1.5.x incompatível com imagem Docker `chromadb/chroma:0.6.x` — servidor fixado em **`chromadb/chroma:1.5.9`**; script recria container se a versão da API for anterior à 1.x
- **Embeddings:** `text-embedding-004` (404 na API atual) substituído por default **`gemini-embedding-001`**; vetores calculados no app e enviados ao Chroma (sem embedding function no servidor)
- **Coleção ausente / alucinação em pagamento:** auto-index no `./scripts/chat.sh`; instruções quando o índice não está disponível; logs RAG ruidosos reduzidos a debug

### Alterado

- README: Chroma Admin, reindex do PDF (`ingest_rag.sh` / `--force`), troubleshooting de versões
- `./install.sh`: passo 12 indexa documentos RAG (idempotente por hash do arquivo)
- Default `GEMINI_MODEL=gemini-3.6-flash` (mantido desde rollback WhatsApp)

## [0.4.0] - 2026-11-02

### Adicionado

- CLI interativa `emporium-chat` e [`scripts/chat.sh`](scripts/chat.sh)
- `ChatService` com histórico persistido, contexto de catálogo PostgreSQL e Gemini
- Leitura automática de `.env`; variáveis `CHAT_HISTORY_LIMIT` e `CHAT_CHANNEL`
- `ensure_env_keys.sh` (sync de chaves ausentes do `.env.example` para `.env`)
- Normalização de histórico Gemini (`llm/history.py`); `CHAT_DEBUG` para diagnóstico

### Alterado

- Papéis de chat alinhados ao Gemini: respostas gravadas como `model` (não `assistant`)
- Migration `003_chat_message_role_model.sql` para histórico legado
- Mensagens de erro não entram mais no contexto enviado ao LLM

## [0.3.0] - 2026-11-02

### Adicionado

- Tabelas `assistant_profile`, `assistant_prompt`, `assistant_chat_message` e migration `002_assistant_tables.sql`
- Seed idempotente Maiara (`db/seed/assistant/default.json`, `seed_assistant.sh`, passo 10 do install)
- Config `Settings`, adapters LLM (`GeminiAdapter`, stub local), `AssistantRepository` e `AssistantService`
- `.env.example`: `ASSISTANT_*`, `LLM_PROVIDER`, `GEMINI_*`
- Dependência `google-genai`

## [0.2.0] - 2026-11-02

### Adicionado

- Importação de seed via Python/psycopg (`import_seed`, `verify`, validação de headers)
- [`db/seed/manifest.json`](db/seed/manifest.json) e truncate + reload a cada `./install.sh`
- Pipeline de migrations (`schema_migrations`, `apply_migrations.sh`, `db/migrations/README.md`)
- Esqueleto Python (`pyproject.toml`, pacote `src/emporium_operations_assistant/`)
- README: política de truncate (dados CSV = sistema externo)

## [0.1.1] - 2026-11-02

### Adicionado

- `install.sh` na raiz com modo `--dry-run` / `preview`
- PostgreSQL via Docker (`ensure_postgres_container.sh`) sem prompts de senha no install padrão
- Scripts `apply_schema.sh` e `scripts/lib/env.sh`
- `.env.example` atualizado (porta 5435, credenciais dev e nomes do container)

## [0.1.0] - 2026-11-02

### Adicionado

- CSVs de seed em `data/` (categorias, clientes, produtos, pedidos, itens e promoções)
- `README.md` com visão do projeto, stack planejada e instruções de setup do PostgreSQL
- `CHANGELOG.md`
- Schema PostgreSQL `emporium_operation` em `db/schema.sql`
- `.env.example` com variáveis de conexão PostgreSQL
- `.gitignore` para Python, ambiente e ferramentas futuras
- Script `scripts/db/create_database.sh` para criação idempotente do banco

[Unreleased]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/releases/tag/v0.1.0
