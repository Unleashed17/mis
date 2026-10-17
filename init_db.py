"""
Database initialization script for WINNIE HARDWARE.

Run this once (or any time you want to reset the database) with:
    python init_db.py

It will:
  1. Create the /database folder if missing.
  2. Create all tables defined in schema.sql.
  3. Create a default administrator account.
  4. Insert a few starter categories and sample hardware products so the
     dashboard is not empty on first login.
"""
import os
import sqlite3
import bcrypt
from config import Config

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")


def run_migrations(conn):
    """
    Safely adds columns that were introduced after the original schema
    (e.g. the eTIMS fields) without breaking existing databases. Checks
    each column's existence first, since SQLite's ALTER TABLE ADD COLUMN
    errors out if the column is already there.
    """
    def existing_columns(table):
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}

    product_columns = {
        "etims_item_cd": "TEXT",
        "etims_item_cls_cd": "TEXT DEFAULT '5059690800'",
        "etims_tax_ty_cd": "TEXT DEFAULT 'B'",
        "etims_synced": "INTEGER NOT NULL DEFAULT 0",
        "etims_synced_at": "TEXT",
    }
    existing = existing_columns("products")
    for col, coltype in product_columns.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE products ADD COLUMN {col} {coltype}")

    sales_columns = {
        "etims_status": "TEXT NOT NULL DEFAULT 'NOT_SUBMITTED'",
        "etims_invc_no": "INTEGER",
        "etims_cu_invc_no": "TEXT",
        "etims_rcpt_sign": "TEXT",
        "etims_intrl_data": "TEXT",
        "etims_sdc_date": "TEXT",
        "etims_result_cd": "TEXT",
        "etims_result_msg": "TEXT",
        "etims_submitted_at": "TEXT",
    }
    existing = existing_columns("sales")
    for col, coltype in sales_columns.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE sales ADD COLUMN {col} {coltype}")

    conn.commit()


def init_database():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

    db_exists = os.path.exists(Config.DATABASE_PATH)

    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_FILE, "r") as f:
        conn.executescript(f.read())

    run_migrations(conn)

    cur = conn.cursor()

    # ---------- eTIMS settings row (single row, created once, disabled by default) ----------
    cur.execute("SELECT id FROM etims_settings WHERE id = 1")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO etims_settings (id, enabled, environment, bhf_id) VALUES (1, 0, 'sandbox', '00')"
        )

    # ---------- Default administrator account ----------
    cur.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cur.fetchone() is None:
        password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, "Shop Administrator", "admin"),
        )
        print("Default administrator account created:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   IMPORTANT: Change this password before real deployment!")

    # ---------- A default sales attendant account (for testing) ----------
    cur.execute("SELECT id FROM users WHERE username = ?", ("attendant",))
    if cur.fetchone() is None:
        password_hash = bcrypt.hashpw("attendant123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("attendant", password_hash, "Sales Attendant", "attendant"),
        )
        print("Default sales attendant account created:")
        print("   Username: attendant")
        print("   Password: attendant123")

    # ---------- Starter categories ----------
    categories = [
        ("Hand Tools", "Hammers, spanners, screwdrivers, pliers, etc."),
        ("Power Tools", "Drills, grinders, saws, and other electric tools"),
        ("Building Materials", "Cement, nails, timber, sand, blocks"),
        ("Plumbing", "Pipes, fittings, taps, valves"),
        ("Electrical", "Cables, switches, sockets, bulbs"),
        ("Paints & Chemicals", "Paints, thinners, adhesives, sealants"),
        ("Fasteners", "Nuts, bolts, screws, nails"),
        ("Safety Gear", "Helmets, gloves, overalls, safety boots"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
        categories,
    )

    # ---------- Sample products (only if the products table is empty) ----------
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT id, name FROM categories")
        cat_map = {row[1]: row[0] for row in cur.fetchall()}

        sample_products = [
            ("Claw Hammer 16oz", "Hand Tools", "Fiberglass handle claw hammer", "BuildPro", "piece", 450, 650, 40, 5, 10, "Nairobi Tools Ltd"),
            ("Cordless Drill 18V", "Power Tools", "18V lithium-ion cordless drill with 2 batteries", "DeWalt", "piece", 6500, 8900, 12, 3, 5, "PowerTech Kenya"),
            ("Cement 50kg", "Building Materials", "Ordinary Portland Cement", "Bamburi", "bag", 650, 780, 200, 30, 50, "Bamburi Cement"),
            ("PVC Pipe 1/2 inch", "Plumbing", "Pressure PVC pipe, 3m length", "Kisumu Pipes", "piece", 180, 250, 150, 20, 40, "Kisumu Pipes Co."),
            ("Electrical Cable 2.5mm (100m roll)", "Electrical", "Copper electrical cable", "Kenwestfal", "roll", 4200, 5200, 8, 2, 5, "Kenwestfal Cables"),
            ("Gloss Paint 4L - White", "Paints & Chemicals", "Oil-based gloss paint", "Crown Paints", "piece", 1600, 2100, 25, 5, 10, "Crown Paints Kenya"),
            ("Assorted Nails 3 inch (1kg)", "Fasteners", "Steel wire nails", "Steelmakers", "kg", 160, 220, 60, 10, 20, "Steelmakers Ltd"),
            ("Safety Helmet", "Safety Gear", "ABS hard hat, adjustable", "SafeGuard", "piece", 350, 500, 30, 5, 10, "SafeGuard Kenya"),
            ("Angle Grinder 4.5 inch", "Power Tools", "850W angle grinder", "Makita", "piece", 3200, 4300, 3, 2, 5, "PowerTech Kenya"),
            ("Padlock 50mm", "Hand Tools", "Brass padlock with 3 keys", "LockTight", "piece", 280, 400, 0, 5, 10, "Nairobi Tools Ltd"),
        ]
        for (name, cat_name, desc, brand, unit, buy, sell, qty, minstock, reorder, supplier) in sample_products:
            cur.execute(
                """INSERT INTO products
                   (name, category_id, description, brand, unit, buying_price, selling_price,
                    quantity, min_stock_level, reorder_quantity, supplier)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, cat_map.get(cat_name), desc, brand, unit, buy, sell, qty, minstock, reorder, supplier),
            )
        print(f"Inserted {len(sample_products)} sample products.")

    conn.commit()
    conn.close()

    if db_exists:
        print("\nDatabase already existed - missing tables/seed data were added if needed.")
    print(f"\nDatabase ready at: {Config.DATABASE_PATH}")


if __name__ == "__main__":
    init_database()
