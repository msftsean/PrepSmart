"""API routes for PrepSmart."""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file

from ..models.crisis_profile import CrisisProfile
from ..services.cache_service import CacheService
from ..services.claude_client import ClaudeClient
from ..services.location_service import LocationService
from ..services.blackboard_service import blackboard_service
from ..agents.coordinator_agent import CoordinatorAgent
from ..utils.logger import setup_logger
from .database import get_db

logger = setup_logger(__name__)

# Initialize services
cache_service = CacheService()
location_service = LocationService()
claude_client = ClaudeClient()
coordinator = CoordinatorAgent(claude_client)


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
            if 'location' in data:
                # If location is a string, convert to dict format
                if isinstance(data['location'], str):
                    # Try to parse as "City, State" or just city name
                    parts = [p.strip() for p in data['location'].split(',')]
                    if len(parts) == 2:
                        data['location'] = {'city': parts[0], 'state': parts[1]}
                    else:
                        data['location'] = {'city': data['location']}

                # If location dict doesn't have geocoding, add it
                if isinstance(data['location'], dict) and not data['location'].get('latitude'):
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

            # Trigger async agent processing in background
            # Flask doesn't natively support async, so we run in a thread
            import threading

            def run_coordinator():
                """Run coordinator in background thread."""
                try:
                    logger.info(f"🎯 Starting coordinator for task_id={task_id}")

                    # Create asyncio event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    # Convert crisis_profile to dict
                    crisis_dict = crisis_profile.model_dump()

                    # Run coordinator
                    completed_blackboard = loop.run_until_complete(
                        coordinator.generate_plan(crisis_dict)
                    )

                    logger.info(f"✅ Coordinator completed for task_id={task_id}")
                    logger.info(f"   Agents completed: {completed_blackboard.agents_completed}")
                    logger.info(f"   Agents failed: {completed_blackboard.agents_failed}")
                    logger.info(f"   Total tokens: {completed_blackboard.total_tokens_used}")
                    logger.info(f"   Total cost: ${completed_blackboard.total_cost_estimate:.4f}")

                    loop.close()

                except Exception as e:
                    logger.error(f"❌ Coordinator error for task_id={task_id}: {e}", exc_info=True)

            # Start background thread
            thread = threading.Thread(target=run_coordinator, daemon=True)
            thread.start()

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
            # Check blackboard for authoritative status
            from ..services.blackboard_service import blackboard_service
            blackboard = blackboard_service.get_blackboard(task_id)

            if not blackboard:
                # Check if task exists in crisis_profiles
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM crisis_profiles WHERE task_id = ?", (task_id,))
                task = cursor.fetchone()
                conn.close()

                if not task:
                    return jsonify({"error": "NotFound", "message": "Task not found"}), 404

                # Task exists but no blackboard yet - still initializing
                return jsonify({
                    "task_id": task_id,
                    "status": "processing",
                    "progress_percentage": 0,
                    "agents": [],
                    "estimated_completion_seconds": 180
                })

            # Get agent logs for detailed progress
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM agent_logs
                WHERE task_id = ?
                ORDER BY started_at
            """, (task_id,))
            logs = cursor.fetchall()
            conn.close()

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

            # Use blackboard status as authoritative source
            status = blackboard.status

            # Calculate progress based on agents completed
            total_agents = 5  # RiskAssessment, SupplyPlanning, ResourceLocator, VideoCurator, Documentation
            completed_agents = len(blackboard.agents_completed)
            failed_agents = len(blackboard.agents_failed)

            if status == "completed":
                progress = 100
            elif status == "failed":
                progress = int((completed_agents / total_agents) * 100) if total_agents > 0 else 0
            else:
                progress = int((completed_agents / total_agents) * 100) if total_agents > 0 else 0

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
        try:
            # Get blackboard from database
            blackboard = blackboard_service.get_blackboard(task_id)

            if not blackboard:
                return jsonify({"error": "NotFound", "message": "Task not found"}), 404

            # Check if plan is complete
            if blackboard.status != "completed":
                return jsonify({
                    "message": "Plan still processing. Check /status endpoint.",
                    "task_id": task_id,
                    "status": blackboard.status,
                    "agents_completed": blackboard.agents_completed,
                    "agents_failed": blackboard.agents_failed
                }), 202

            # Return complete plan
            return jsonify({
                "task_id": task_id,
                "status": "completed",
                "crisis_profile": blackboard.crisis_profile,
                "risk_assessment": blackboard.risk_assessment,
                "supply_plan": blackboard.supply_plan,
                "economic_plan": blackboard.economic_plan,
                "resource_locations": blackboard.resource_locations,
                "video_recommendations": blackboard.video_recommendations,
                "complete_plan": blackboard.complete_plan,
                "pdf_path": blackboard.pdf_path,
                "execution_time_seconds": blackboard.total_execution_seconds,
                "total_tokens_used": blackboard.total_tokens_used,
                "total_cost_estimate": blackboard.total_cost_estimate,
                "agents_completed": blackboard.agents_completed,
                "agents_failed": blackboard.agents_failed
            })

        except Exception as e:
            logger.error(f"Error getting result for {task_id}: {e}")
            return jsonify({"error": "InternalError", "message": "Failed to get result"}), 500

    @app.route('/api/crisis/<task_id>/pdf', methods=['GET'])
    def download_pdf(task_id: str):
        """Download crisis plan PDF."""
        try:
            # Get blackboard from database
            blackboard = blackboard_service.get_blackboard(task_id)

            if not blackboard:
                return jsonify({"error": "NotFound", "message": "Task not found"}), 404

            # Check if PDF is ready
            if not blackboard.pdf_path:
                return jsonify({
                    "message": "PDF generation in progress. Retry in 5 seconds.",
                    "task_id": task_id,
                    "status": blackboard.status
                }), 202

            # Check if PDF file exists
            pdf_path = Path(blackboard.pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return jsonify({
                    "error": "NotFound",
                    "message": "PDF file not found on server"
                }), 404

            # Serve PDF file
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"crisis_plan_{task_id}.pdf"
            )

        except Exception as e:
            logger.error(f"Error downloading PDF for {task_id}: {e}")
            return jsonify({"error": "InternalError", "message": "Failed to download PDF"}), 500

    logger.info("API routes registered")
