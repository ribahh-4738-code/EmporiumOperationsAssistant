-- Emporium Operations Assistant — relational schema (derived from data/*.csv)
-- Apply while connected to database: emporium_operation

BEGIN;

-- ---------------------------------------------------------------------------
-- categories
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT
);

COMMENT ON TABLE categories IS 'Product categories for the emporium catalog';
COMMENT ON COLUMN categories.category_id IS 'Stable category identifier from seed data';

-- ---------------------------------------------------------------------------
-- customers
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    phone       VARCHAR(32),
    email       VARCHAR(255),
    city        VARCHAR(128)
);

COMMENT ON TABLE customers IS 'Registered customers';

-- ---------------------------------------------------------------------------
-- products
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id      INTEGER PRIMARY KEY,
    price_brl       NUMERIC(12, 2) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES categories (category_id),
    description     TEXT,
    stock_quantity  INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(32) NOT NULL,
    specs           JSONB,
    created_at      DATE
);

CREATE INDEX IF NOT EXISTS idx_products_category_id ON products (category_id);

COMMENT ON TABLE products IS 'Catalog products with JSON specifications';
COMMENT ON COLUMN products.specs IS 'Structured product attributes (JSON from CSV)';

-- ---------------------------------------------------------------------------
-- orders
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id            INTEGER PRIMARY KEY,
    customer_id         INTEGER NOT NULL REFERENCES customers (customer_id),
    order_date          DATE NOT NULL,
    status              VARCHAR(32) NOT NULL,
    total_brl           NUMERIC(12, 2) NOT NULL,
    payment_method      VARCHAR(64) NOT NULL,
    tracking_code       VARCHAR(64),
    estimated_delivery  DATE,
    notes               TEXT
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status);

COMMENT ON TABLE orders IS 'Customer purchase orders';

-- ---------------------------------------------------------------------------
-- order_items
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_id   INTEGER NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items (product_id);

COMMENT ON TABLE order_items IS 'Line items linking orders to products';

-- ---------------------------------------------------------------------------
-- promotions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS promotions (
    promotion_id     INTEGER PRIMARY KEY,
    product_id       INTEGER NOT NULL REFERENCES products (product_id),
    discount_percent SMALLINT NOT NULL CHECK (discount_percent >= 0 AND discount_percent <= 100),
    description      VARCHAR(255),
    is_active        BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_promotions_product_id ON promotions (product_id);
CREATE INDEX IF NOT EXISTS idx_promotions_is_active ON promotions (is_active);

COMMENT ON TABLE promotions IS 'Product-level promotional discounts';

COMMIT;
