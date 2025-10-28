"""Flask application initialization for PrepSmart."""

from flask import Flask
from flask_cors import CORS

from ..utils.config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app() -> Flask:
    """
    Create and configure Flask application.

    Returns:
        Configured Flask app
    """
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = settings.flask_secret_key
    app.config['DEBUG'] = settings.flask_debug

    # CORS configuration
    allowed_origins = settings.allowed_origins
    if allowed_origins:
        origins = [origin.strip() for origin in allowed_origins.split(',')]
        CORS(app, origins=origins)
    else:
        # Development: allow all origins
        CORS(app)

    # Register routes (import here to avoid circular import)
    from .routes import register_routes
    register_routes(app)

    logger.info(f"Flask app created (debug={app.config['DEBUG']})")

    return app


# Import database functions from separate module to avoid circular imports
from .database import init_db, get_db


# Create app instance
app = create_app()


if __name__ == '__main__':
    # Initialize database if running directly
    init_db()

    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=settings.flask_debug
    )
