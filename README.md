# Emporium Operations Assistant

Assistente conversacional para operações de um emporium de instrumentos musicais. O sistema utiliza a persona **Maiara** e, nas fases futuras, responderá via **linha de comando** e **WhatsApp**.

## Stack planejada

| Componente | Uso |
|------------|-----|
| **Python** | Aplicação principal e integrações |
| **PostgreSQL** | Banco relacional (catálogo, pedidos, clientes, configurações) |
| **ChromaDB** | Busca semântica sobre conteúdo do emporium |
| **WhatsApp** | Canal de atendimento (configuração posterior) |

## Configuração

- Variáveis de ambiente sensíveis e de infraestrutura ficam no arquivo **`.env`** (use [`.env.example`](.env.example) como modelo).
- Parâmetros operacionais do assistente — por exemplo **`system_prompt`** — serão armazenados no **PostgreSQL** em um marco futuro.

## Marco 1 (v0.1.0) — Documentação e banco de dados

**Entregue neste marco:**

- Dados de seed em [`data/`](data/) (CSV)
- Schema PostgreSQL em [`db/schema.sql`](db/schema.sql)
- Script auxiliar para criar o banco [`scripts/db/create_database.sh`](scripts/db/create_database.sh)
- Documentação (`README`, `CHANGELOG`)

**Próximo marco (previsto):**

- Estrutura base do projeto Python
- Script de importação dos CSVs para o PostgreSQL
- Validação de contagens pós-importação

## Pré-requisitos

- **Docker** (PostgreSQL do projeto roda em container; não é necessário informar senha manualmente)
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
3. Garante o banco `emporium_operation` e aplica `db/schema.sql`
4. Lista as tabelas criadas (esperado: **6 tabelas**, ainda **sem dados** até a importação do marco 2)

Conexão padrão após o install: `localhost:5435`, usuário/senha/banco conforme `.env`.

## Setup manual (opcional, sem Docker)

Se preferir PostgreSQL no host, ajuste `.env` (por exemplo porta `5432`) e use:

```bash
./scripts/db/create_database.sh
./scripts/db/apply_schema.sh
```

## Estrutura do repositório

```
EmporiumOperationsAssistant/
├── CHANGELOG.md
├── README.md
├── install.sh            # Instalação incremental (Docker + DB)
├── data/                 # CSVs de seed
├── db/
│   └── schema.sql        # DDL PostgreSQL
└── scripts/
    ├── lib/
    │   └── env.sh
    └── db/
        ├── apply_schema.sh
        ├── create_database.sh
        └── ensure_postgres_container.sh
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
