"""
WINNIE HARDWARE - Inventory Management System
Main Flask application entry point.

Run with:  python app.py
"""
import os
from flask import Flask, session, jsonify
from config import Config
import database

from routes.pages import pages_bp
from routes.auth import auth_bp
from routes.api_products import products_api, categories_api
from routes.api_customers import customers_api
from routes.api_sales import sales_api
from routes.api_reports import reports_api
from routes.api_users import users_api
from routes.api_etims import etims_api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure the database file actually exists before the app starts.
    if not os.path.exists(Config.DATABASE_PATH):
        print("No database found - creating one automatically...")
        from init_db import init_database
        init_database()

    database.init_app(app)

    # Register page routes (server-rendered HTML)
    app.register_blueprint(pages_bp)

    # Register JSON API routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_api)
    app.register_blueprint(categories_api)
    app.register_blueprint(customers_api)
    app.register_blueprint(sales_api)
    app.register_blueprint(reports_api)
    app.register_blueprint(users_api)
    app.register_blueprint(etims_api)

    @app.get("/api/me")
    def me():
        """Lets the frontend know who is logged in and what role they have."""
        if "user_id" not in session:
            return jsonify({"success": False}), 401
        return jsonify({
            "success": True,
            "data": {
                "user_id": session.get("user_id"),
                "username": session.get("username"),
                "full_name": session.get("full_name"),
                "role": session.get("role"),
            }
        })

    # ---------- Friendly error handlers so the app never crashes on the user ----------
    @app.errorhandler(404)
    def not_found(e):
        if "/api/" in str(e):
            return jsonify({"success": False, "message": "Resource not found."}), 404
        return "Page not found. <a href='/'>Go home</a>", 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "An unexpected server error occurred. Please try again."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
