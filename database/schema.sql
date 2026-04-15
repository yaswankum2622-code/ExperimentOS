CREATE TABLE IF NOT EXISTS events (
    event_id      INTEGER PRIMARY KEY,
    user_id       INTEGER NOT NULL,
    event_type    TEXT NOT NULL CHECK(event_type IN ('view','add_to_cart','purchase')),
    timestamp     DATETIME NOT NULL,
    invoice_id    TEXT,
    product_id    TEXT,
    revenue       REAL DEFAULT 0,
    country       TEXT,
    variant       TEXT CHECK(variant IN ('A','B')),
    event_date    DATE GENERATED ALWAYS AS (DATE(timestamp)) VIRTUAL
);

CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    first_seen     DATE NOT NULL,
    country        TEXT,
    variant        TEXT CHECK(variant IN ('A','B')),
    total_orders   INTEGER DEFAULT 0,
    total_revenue  REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id     TEXT PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    timestamp      DATETIME NOT NULL,
    total_revenue  REAL NOT NULL,
    item_count     INTEGER NOT NULL,
    country        TEXT,
    variant        TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_variant ON events(variant);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
