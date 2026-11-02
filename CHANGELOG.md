# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-11-02

### Adicionado

- CSVs de seed em `data/` (categorias, clientes, produtos, pedidos, itens e promoções)
- `README.md` com visão do projeto, stack planejada e instruções de setup do PostgreSQL
- `CHANGELOG.md`
- Schema PostgreSQL `emporium_operation` em `db/schema.sql`
- `.env.example` com variáveis de conexão PostgreSQL
- `.gitignore` para Python, ambiente e ferramentas futuras
- Script `scripts/db/create_database.sh` para criação idempotente do banco

[0.1.0]: https://github.com/ribahh-4738-code/EmporiumOperationsAssistant/releases/tag/v0.1.0
