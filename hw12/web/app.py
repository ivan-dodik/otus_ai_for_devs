"""
Flask application factory for the anime recommendation agent web UI.
"""

from flask import Flask

from config import config, setup_logging
from web.routes import web_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = "anime-agent-secret-key-change-in-production"

    app.register_blueprint(web_bp)

    return app


if __name__ == "__main__":
    setup_logging()
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )
