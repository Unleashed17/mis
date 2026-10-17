-- WINNIE HARDWARE Inventory Management System
-- Database schema (SQLite)

PRAGMA foreign_keys = ON;

-- ===================== USERS =====================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'attendant')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ===================== CATEGORIES =====================
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- ===================== PRODUCTS =====================
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    description TEXT,
    brand TEXT,
    unit TEXT NOT NULL DEFAULT 'piece',        -- piece, kg, meter, litre, bag, roll, box, etc.
    buying_price REAL NOT NULL DEFAULT 0,
    selling_price REAL NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL DEFAULT 0,
    min_stock_level INTEGER NOT NULL DEFAULT 5,
    reorder_quantity INTEGER NOT NULL DEFAULT 10,
    supplier TEXT,
    date_added TEXT NOT NULL DEFAULT (datetime('now')),
    last_updated TEXT NOT NULL DEFAULT (datetime('now')),
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ===================== CUSTOMERS =====================
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    address TEXT,
    date_registered TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ===================== SALES =====================
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    user_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL DEFAULT (datetime('now')),
    total_amount REAL NOT NULL DEFAULT 0,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('Cash', 'M-Pesa', 'Card')),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ===================== SALE ITEMS =====================
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ===================== STOCK MOVEMENTS =====================
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
    quantity INTEGER NOT NULL,
    reason TEXT,                -- e.g. 'New stock received', 'Sale #12', 'Stock correction'
    user_id INTEGER,
    movement_date TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON stock_movements(product_id);

-- ===================== KRA eTIMS =====================
-- Stores the single set of eTIMS/OSCU credentials for this shop (one branch).
-- These values come from KRA after you register for eTIMS OSCU - see README.
CREATE TABLE IF NOT EXISTS etims_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),   -- enforce a single settings row
    enabled INTEGER NOT NULL DEFAULT 0,       -- master on/off switch
    environment TEXT NOT NULL DEFAULT 'sandbox' CHECK (environment IN ('sandbox', 'production')),
    tin TEXT,               -- KRA PIN, e.g. A123456789Z
    bhf_id TEXT DEFAULT '00',  -- Branch ID ('00' = head office, given by KRA)
    device_serial TEXT,     -- a serial number you choose for this install, e.g. WINNIE-POS-01
    cmc_key TEXT,            -- communication key returned by KRA after device activation
    device_initialized INTEGER NOT NULL DEFAULT 0,
    last_item_sync TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- NOTE: the eTIMS columns added to "products" and "sales" (etims_item_cd,
-- etims_status, etims_rcpt_sign, etc.) are NOT created here. SQLite's
-- ALTER TABLE ADD COLUMN fails if a column already exists, which would break
-- re-running this script against a database that already has them. They are
-- instead added safely (checked first) by run_migrations() in init_db.py,
-- which is always called before the app starts.
