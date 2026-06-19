from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

CATALOG = [
    {"id": 1, "name": "workflow-engine", "category": "platform"},
    {"id": 2, "name": "api-gateway", "category": "backend"},
    {"id": 3, "name": "search-service", "category": "backend"},
    {"id": 4, "name": "ui-portal", "category": "frontend"},
]


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["APP_NAME"] = os.getenv("APP_NAME", "argo-workflows-demo-app")
    app.config["APP_ENV"] = os.getenv("APP_ENV", "dev")
    app.config["APP_VERSION"] = os.getenv("APP_VERSION", "0.1.0")

    @app.get("/")
    def index() -> Any:
        return jsonify(
            {
                "app": app.config["APP_NAME"],
                "environment": app.config["APP_ENV"],
                "version": app.config["APP_VERSION"],
                "message": "Demo application for Argo WorkflowTemplates.",
            }
        )

    @app.get("/health")
    def health() -> Any:
        return jsonify(
            {
                "status": "ok",
                "app": app.config["APP_NAME"],
                "environment": app.config["APP_ENV"],
                "version": app.config["APP_VERSION"],
            }
        )

    @app.get("/api/catalog")
    def catalog() -> Any:
        return jsonify({"items": CATALOG, "count": len(CATALOG)})

    @app.get("/api/search")
    def search() -> Any:
        query = request.args.get("q", "").strip().lower()
        if not query:
            return jsonify({"items": CATALOG, "count": len(CATALOG), "query": query})

        filtered = [item for item in CATALOG if query in item["name"] or query in item["category"]]
        return jsonify({"items": filtered, "count": len(filtered), "query": query})

    return app
