#!/usr/bin/env python3
"""
Alpha Evolve Dashboard — Flask web app for tracking evolutionary runs.

Usage:
    source venv/bin/activate
    python dashboard/app.py              # http://localhost:5000
    python dashboard/app.py --port 8080  # custom port
    python dashboard/app.py --debug      # hot reload
"""

import argparse
import sys
from pathlib import Path

from flask import Flask

# Ensure the project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.routes import api_bp, pages_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    return app


def main():
    parser = argparse.ArgumentParser(description="Alpha Evolve Dashboard")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    from dashboard.data.config import get_project_root
    root = get_project_root()

    print(f"Alpha Evolve Dashboard: http://{args.host}:{args.port}")
    print(f"Project root: {root}")

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
