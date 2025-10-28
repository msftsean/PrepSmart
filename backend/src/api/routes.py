"""API routes for PrepSmart."""

import json
import uuid
from datetime import datetime

from flask import Flask, jsonify, request

from ..models.crisis_profile import CrisisProfile
from ..services.cache_service import CacheService
from ..services.claude_client import ClaudeClient
from ..services.location_service import LocationService
from ..utils.logger import setup_logger
from .app import get_db

logger = setup_logger(__name__)

# Initialize services
cache_service = CacheService()
location_service = LocationService()
claude_client = ClaudeClient()


def register_routes(app: Flask) -> None:
    """
    Register all API routes.

    Args:
        app: Flask application
    """

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        # Test Claude API connection
        claude_status = "up" if claude_client.test_connection() else "down"

        # Test database connection
        try:
            conn = get_db()
            conn.execute("SELECT 1")
            conn.close()
            db_status = "up"
        except Exception:
            db_status = "down"

        status = "healthy" if claude_status == "up" and db_status == "up" else "degraded"

        return jsonify({
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "dependencies": {
                "claude_api": claude_status,
                "database": db_status
            }
        })

    @app.route('/api/crisis/validate-location', methods=['POST'])
    def validate_location():
        """Validate and geocode location."""
        data = request.json

        if not data:
            return jsonify({"error": "ValidationError", "message": "Request body required"}), 400

        # Validate location
        location = location_service.validate_and_geocode(data)

        if not location:
            return jsonify({
                "error": "ValidationError",
                "message": "Invalid location. Please provide valid ZIP code or city/state."
            }), 400

        return jsonify({
            "valid": True,
            "location": location
        })

    @app.route('/api/crisis/start', methods=['POST'])
    def start_crisis_plan():
        """Start crisis plan generation."""
        data = request.json

        if not data:
            return jsonify({"error": "ValidationError", "message": "Request body required"}), 400

        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            data['task_id'] = task_id
            data['created_at'] = datetime.utcnow()

            # Validate and geocode location if needed
            if 'location' in data and not data['location'].get('latitude'):
                location = location_service.validate_and_geocode(data['location'])
                if location:
                    data['location'] = location

            # Validate with Pydantic
            crisis_profile = CrisisProfile(**data)

            # Store in database
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO crisis_profiles (
                    task_id, created_at, crisis_mode, specific_threat,
                    location_json, household_json, housing_type, budget_tier,
                    financial_situation_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crisis_profile.task_id,
                crisis_profile.created_at,
                crisis_profile.crisis_mode,
                crisis_profile.specific_threat,
                json.dumps(crisis_profile.location),
                json.dumps(crisis_profile.household),
                crisis_profile.housing_type,
                crisis_profile.budget_tier,
                json.dumps(crisis_profile.financial_situation) if crisis_profile.financial_situation else None,
                'processing'
            ))
            conn.commit()
            conn.close()

            logger.info(f"Created crisis plan task: {task_id}")

            # TODO: Trigger async agent processing here
            # For now, return task ID immediately

            return jsonify({
                "task_id": task_id,
                "status": "processing",
                "message": "Crisis plan generation started. Use task_id to check status.",
                "estimated_time_seconds": 180
            }), 202

        except ValueError as e:
            return jsonify({"error": "ValidationError", "message": str(e)}), 400
        except Exception as e:
            logger.error(f"Error starting crisis plan: {e}")
            return jsonify({"error": "InternalError", "message": "Failed to start plan generation"}), 500

    @app.route('/api/crisis/<task_id>/status', methods=['GET'])
    def get_crisis_status(task_id: str):
        """Get crisis plan generation status."""
        try:
            # Get agent logs for this task
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM agent_logs
                WHERE task_id = ?
                ORDER BY started_at
            """, (task_id,))
            logs = cursor.fetchall()
            conn.close()

            if not logs and task_id:
                # Check if task exists
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM crisis_profiles WHERE task_id = ?", (task_id,))
                task = cursor.fetchone()
                conn.close()

                if not task:
                    return jsonify({"error": "NotFound", "message": "Task not found"}), 404

            # Convert logs to dict
            agents = []
            for log in logs:
                agents.append({
                    "agent_name": log['agent_name'],
                    "agent_type": log['agent_type'],
                    "status": log['status'],
                    "current_task_description": log['current_task_description'],
                    "progress_percentage": log['progress_percentage'],
                    "started_at": log['started_at'],
                    "completed_at": log['completed_at'],
                    "error_message": log['error_message']
                })

            # Determine overall status
            if not agents:
                status = "processing"
                progress = 0
            elif all(a['status'] == 'complete' for a in agents):
                status = "completed"
                progress = 100
            elif any(a['status'] == 'error' for a in agents):
                status = "failed"
                progress = sum(a['progress_percentage'] for a in agents) // len(agents)
            else:
                status = "processing"
                progress = sum(a['progress_percentage'] for a in agents) // len(agents) if agents else 0

            return jsonify({
                "task_id": task_id,
                "status": status,
                "progress_percentage": progress,
                "agents": agents,
                "estimated_completion_seconds": None
            })

        except Exception as e:
            logger.error(f"Error getting status for {task_id}: {e}")
            return jsonify({"error": "InternalError", "message": "Failed to get status"}), 500

    @app.route('/api/crisis/<task_id>/result', methods=['GET'])
    def get_crisis_result(task_id: str):
        """Get complete crisis plan."""
        # TODO: Implement full result retrieval with agent outputs
        return jsonify({
            "message": "Plan still processing. Check /status endpoint.",
            "task_id": task_id
        }), 202

    @app.route('/api/crisis/<task_id>/pdf', methods=['GET'])
    def download_pdf(task_id: str):
        """Download crisis plan PDF."""
        # TODO: Implement PDF generation
        return jsonify({
            "message": "PDF generation in progress. Retry in 5 seconds.",
            "task_id": task_id
        }), 202

    logger.info("API routes registered")
