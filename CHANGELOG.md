# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Alterado

- Default `GEMINI_MODEL=gemini-3.6-flash` em `.env.example` e `config.py` (CLI only; WhatsApp removido do escopo)

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

[Unreleased]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/releases/tag/v0.1.0
