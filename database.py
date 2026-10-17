"""
Database connection helper for WINNIE HARDWARE.
Uses Python's built-in sqlite3 module - no external DB driver needed.
"""
import sqlite3
from flask import g, current_app


def get_db():
    """
    Returns a SQLite connection stored on Flask's application context (g),
    so the same request reuses one connection instead of opening many.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register the close_db function to run after every request."""
    app.teardown_appcontext(close_db)
