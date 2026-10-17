"""
Configuration settings for WINNIE HARDWARE Inventory Management System.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key used to sign session cookies.
    # In a real deployment, set this via an environment variable instead.
    SECRET_KEY = os.environ.get("SECRET_KEY", "winnie-hardware-dev-secret-change-this")

    # Path to the SQLite database file
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "winnie_hardware.db")

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 hours

    # Low stock is anything at or below the product's min_stock_level
    CURRENCY_SYMBOL = "KSh"

    # ---------- KRA eTIMS (OSCU) ----------
    # Official KRA server addresses (OSCU Specification Document v2.0, April 2023).
    # Do not change unless KRA publishes new addresses.
    ETIMS_SANDBOX_BASE_URL = "https://etims-api-sbx.kra.go.ke/etims-api"
    ETIMS_PRODUCTION_BASE_URL = "https://etims-api.kra.go.ke/etims-api"

    # Requests to KRA's servers time out after this many seconds rather than
    # hanging the sale screen if KRA is slow/unreachable.
    ETIMS_TIMEOUT_SECONDS = 15
