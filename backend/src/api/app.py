"""Flask application initialization for PrepSmart."""

import sqlite3
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from ..utils.config import settings
from ..utils.logger import setup_logger
from .routes import register_routes

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

    # Register routes
    register_routes(app)

    logger.info(f"Flask app created (debug={app.config['DEBUG']})")

    return app


def init_db() -> None:
    """Initialize SQLite database with schema."""
    db_path = Path(settings.database_url.replace('sqlite:///', ''))

    logger.info(f"Initializing database at {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create crisis_profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crisis_profiles (
            task_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            crisis_mode TEXT NOT NULL,
            specific_threat TEXT NOT NULL,
            location_json TEXT NOT NULL,
            household_json TEXT NOT NULL,
            housing_type TEXT NOT NULL,
            budget_tier INTEGER NOT NULL,
            financial_situation_json TEXT,
            status TEXT DEFAULT 'processing',
            completed_at TIMESTAMP
        )
    """)

    # Create index on created_at for querying recent tasks
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_crisis_created
        ON crisis_profiles(created_at)
    """)

    # Create index on status
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_crisis_status
        ON crisis_profiles(status)
    """)

    # Create agent_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            log_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            status TEXT NOT NULL,
            current_task_description TEXT NOT NULL,
            progress_percentage INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            execution_time_seconds REAL,
            error_message TEXT,
            messages_json TEXT,
            tokens_used INTEGER,
            cost_estimate REAL,
            FOREIGN KEY (task_id) REFERENCES crisis_profiles(task_id)
        )
    """)

    # Create indices for agent_logs
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_logs_task
        ON agent_logs(task_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_logs_status
        ON agent_logs(status)
    """)

    # Create blackboards table for multi-agent coordination
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blackboards (
            task_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            crisis_profile_json TEXT NOT NULL,
            risk_assessment_json TEXT,
            supply_plan_json TEXT,
            emergency_plan_json TEXT,
            economic_plan_json TEXT,
            resource_locations_json TEXT,
            video_recommendations_json TEXT,
            complete_plan_json TEXT,
            pdf_path TEXT,

            status TEXT DEFAULT 'initialized',
            agents_completed_json TEXT,
            agents_failed_json TEXT,

            execution_start TIMESTAMP,
            execution_end TIMESTAMP,
            total_execution_seconds REAL,

            total_tokens_used INTEGER DEFAULT 0,
            total_cost_estimate REAL DEFAULT 0.0,

            errors_json TEXT,

            FOREIGN KEY (task_id) REFERENCES crisis_profiles(task_id)
        )
    """)

    # Create indices for blackboards
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_blackboard_status
        ON blackboards(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_blackboard_updated
        ON blackboards(updated_at)
    """)

    conn.commit()
    conn.close()

    logger.info("Database initialized successfully (crisis_profiles, agent_logs, blackboards)")


def get_db() -> sqlite3.Connection:
    """
    Get database connection.

    Returns:
        SQLite connection
    """
    db_path = settings.database_url.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


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
