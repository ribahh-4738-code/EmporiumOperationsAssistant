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

- PostgreSQL 14+ (cliente `psql` no PATH)
- Bash (para o script de criação do banco)

## Setup rápido do banco

1. Clone o repositório e entre na pasta do projeto.

2. Copie o exemplo de ambiente e ajuste credenciais:

   ```bash
   cp .env.example .env
   ```

3. Crie o banco de dados:

   ```bash
   chmod +x scripts/db/create_database.sh
   ./scripts/db/create_database.sh
   ```

4. Aplique o schema (conectado ao banco `emporium_operation`):

   ```bash
   psql -d emporium_operation -f db/schema.sql
   ```

5. Verifique as tabelas (esperado: **6 tabelas**, ainda **sem dados** até a importação do marco 2):

   ```bash
   psql -d emporium_operation -c "\dt"
   ```

## Estrutura do repositório

```
EmporiumOperationsAssistant/
├── CHANGELOG.md
├── README.md
├── data/                 # CSVs de seed
├── db/
│   └── schema.sql        # DDL PostgreSQL
└── scripts/
    └── db/
        └── create_database.sh
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
