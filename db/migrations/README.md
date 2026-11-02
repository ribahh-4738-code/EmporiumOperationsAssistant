# Database migrations

Incremental DDL changes for databases that already exist. Fresh installs get the full baseline from [`../schema.sql`](../schema.sql).

## When CSV structure changes

If seed CSV headers or columns change:

1. Update [`../seed/manifest.json`](../seed/manifest.json) (`columns`, `expected_rows`).
2. Update [`../schema.sql`](../schema.sql) so new installs match the CSV contract.
3. Add a new file here: `NNN_short_description.sql` (e.g. `002_add_products_sku.sql`).
4. Re-run [`../../install.sh`](../../install.sh).

`install.sh` applies pending migrations, then truncates seed tables and reloads from `data/*.csv`.

Do **not** put seed `INSERT` data in migration files or in `schema.sql`.
