"""
Blackboard Service: Atomic read/write operations for the blackboard pattern.

Provides thread-safe operations to create, read, update blackboards in the database.
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..models.blackboard import Blackboard
from ..utils.config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BlackboardService:
    """Service for managing blackboard state in database with atomic operations."""

    def __init__(self) -> None:
        """Initialize blackboard service."""
        self.db_path = Path(settings.database_url.replace('sqlite:///', ''))

    def _get_conn(self) -> sqlite3.Connection:
        """
        Get database connection.

        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_blackboard(self, crisis_profile: dict) -> Blackboard:
        """
        Create a new blackboard with initial crisis profile.

        Args:
            crisis_profile: User's crisis scenario (CrisisProfile as dict)

        Returns:
            Newly created Blackboard instance

        Raises:
            ValueError: If task_id already exists
        """
        task_id = crisis_profile.get('task_id')
        if not task_id:
            raise ValueError("crisis_profile must include task_id")

        blackboard = Blackboard(
            task_id=task_id,
            crisis_profile=crisis_profile,
            status="initialized"
        )

        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            # Serialize crisis_profile with datetime handling (default=str converts datetime to ISO format)
            crisis_profile_json = json.dumps(blackboard.crisis_profile, default=str)

            cursor.execute("""
                INSERT INTO blackboards (
                    task_id,
                    created_at,
                    updated_at,
                    crisis_profile_json,
                    status,
                    agents_completed_json,
                    agents_failed_json,
                    total_tokens_used,
                    total_cost_estimate,
                    errors_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                blackboard.task_id,
                blackboard.created_at.isoformat(),
                blackboard.updated_at.isoformat(),
                crisis_profile_json,
                blackboard.status,
                json.dumps(blackboard.agents_completed),
                json.dumps(blackboard.agents_failed),
                blackboard.total_tokens_used,
                blackboard.total_cost_estimate,
                json.dumps(blackboard.errors)
            ))

            conn.commit()
            logger.info(f"Created blackboard for task_id={task_id}")

            return blackboard

        except sqlite3.IntegrityError as e:
            logger.error(f"Blackboard already exists for task_id={task_id}: {e}")
            raise ValueError(f"Blackboard already exists for task_id={task_id}")
        finally:
            conn.close()

    def get_blackboard(self, task_id: str) -> Optional[Blackboard]:
        """
        Get blackboard by task_id.

        Args:
            task_id: Unique task identifier

        Returns:
            Blackboard instance if found, None otherwise
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM blackboards WHERE task_id = ?
            """, (task_id,))

            row = cursor.fetchone()

            if not row:
                logger.warning(f"Blackboard not found for task_id={task_id}")
                return None

            # Convert row to dictionary
            data = dict(row)

            # Parse JSON fields
            blackboard = Blackboard(
                task_id=data['task_id'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at']),
                crisis_profile=json.loads(data['crisis_profile_json']) if data['crisis_profile_json'] else None,
                risk_assessment=json.loads(data['risk_assessment_json']) if data['risk_assessment_json'] else None,
                supply_plan=json.loads(data['supply_plan_json']) if data['supply_plan_json'] else None,
                emergency_plan=json.loads(data['emergency_plan_json']) if data['emergency_plan_json'] else None,
                economic_plan=json.loads(data['economic_plan_json']) if data['economic_plan_json'] else None,
                resource_locations=json.loads(data['resource_locations_json']) if data['resource_locations_json'] else None,
                video_recommendations=json.loads(data['video_recommendations_json']) if data['video_recommendations_json'] else None,
                complete_plan=json.loads(data['complete_plan_json']) if data['complete_plan_json'] else None,
                pdf_path=data['pdf_path'],
                status=data['status'],
                agents_completed=json.loads(data['agents_completed_json']) if data['agents_completed_json'] else [],
                agents_failed=json.loads(data['agents_failed_json']) if data['agents_failed_json'] else [],
                execution_start=datetime.fromisoformat(data['execution_start']) if data['execution_start'] else None,
                execution_end=datetime.fromisoformat(data['execution_end']) if data['execution_end'] else None,
                total_execution_seconds=data['total_execution_seconds'],
                total_tokens_used=data['total_tokens_used'],
                total_cost_estimate=data['total_cost_estimate'],
                errors=json.loads(data['errors_json']) if data['errors_json'] else []
            )

            return blackboard

        finally:
            conn.close()

    def update_blackboard(self, blackboard: Blackboard) -> None:
        """
        Update blackboard atomically in database.

        Args:
            blackboard: Blackboard instance with updated state

        Raises:
            ValueError: If blackboard doesn't exist
        """
        blackboard.updated_at = datetime.utcnow()

        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE blackboards SET
                    updated_at = ?,
                    risk_assessment_json = ?,
                    supply_plan_json = ?,
                    emergency_plan_json = ?,
                    economic_plan_json = ?,
                    resource_locations_json = ?,
                    video_recommendations_json = ?,
                    complete_plan_json = ?,
                    pdf_path = ?,
                    status = ?,
                    agents_completed_json = ?,
                    agents_failed_json = ?,
                    execution_start = ?,
                    execution_end = ?,
                    total_execution_seconds = ?,
                    total_tokens_used = ?,
                    total_cost_estimate = ?,
                    errors_json = ?
                WHERE task_id = ?
            """, (
                blackboard.updated_at.isoformat(),
                json.dumps(blackboard.risk_assessment) if blackboard.risk_assessment else None,
                json.dumps(blackboard.supply_plan) if blackboard.supply_plan else None,
                json.dumps(blackboard.emergency_plan) if blackboard.emergency_plan else None,
                json.dumps(blackboard.economic_plan) if blackboard.economic_plan else None,
                json.dumps(blackboard.resource_locations) if blackboard.resource_locations else None,
                json.dumps(blackboard.video_recommendations) if blackboard.video_recommendations else None,
                json.dumps(blackboard.complete_plan) if blackboard.complete_plan else None,
                blackboard.pdf_path,
                blackboard.status,
                json.dumps(blackboard.agents_completed),
                json.dumps(blackboard.agents_failed),
                blackboard.execution_start.isoformat() if blackboard.execution_start else None,
                blackboard.execution_end.isoformat() if blackboard.execution_end else None,
                blackboard.total_execution_seconds,
                blackboard.total_tokens_used,
                blackboard.total_cost_estimate,
                json.dumps(blackboard.errors),
                blackboard.task_id
            ))

            if cursor.rowcount == 0:
                raise ValueError(f"Blackboard not found for task_id={blackboard.task_id}")

            conn.commit()
            logger.info(f"Updated blackboard for task_id={blackboard.task_id}, status={blackboard.status}")

        finally:
            conn.close()

    def delete_blackboard(self, task_id: str) -> bool:
        """
        Delete blackboard by task_id.

        Args:
            task_id: Unique task identifier

        Returns:
            True if deleted, False if not found
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM blackboards WHERE task_id = ?
            """, (task_id,))

            deleted = cursor.rowcount > 0
            conn.commit()

            if deleted:
                logger.info(f"Deleted blackboard for task_id={task_id}")
            else:
                logger.warning(f"Blackboard not found for deletion: task_id={task_id}")

            return deleted

        finally:
            conn.close()

    def list_blackboards(self, status: Optional[str] = None, limit: int = 100) -> list[Blackboard]:
        """
        List blackboards, optionally filtered by status.

        Args:
            status: Filter by status (initialized, processing, completed, failed)
            limit: Maximum number of results

        Returns:
            List of Blackboard instances
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            if status:
                cursor.execute("""
                    SELECT * FROM blackboards
                    WHERE status = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM blackboards
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()

            blackboards = []
            for row in rows:
                data = dict(row)
                blackboard = Blackboard(
                    task_id=data['task_id'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    crisis_profile=json.loads(data['crisis_profile_json']) if data['crisis_profile_json'] else None,
                    risk_assessment=json.loads(data['risk_assessment_json']) if data['risk_assessment_json'] else None,
                    supply_plan=json.loads(data['supply_plan_json']) if data['supply_plan_json'] else None,
                    emergency_plan=json.loads(data['emergency_plan_json']) if data['emergency_plan_json'] else None,
                    economic_plan=json.loads(data['economic_plan_json']) if data['economic_plan_json'] else None,
                    resource_locations=json.loads(data['resource_locations_json']) if data['resource_locations_json'] else None,
                    video_recommendations=json.loads(data['video_recommendations_json']) if data['video_recommendations_json'] else None,
                    complete_plan=json.loads(data['complete_plan_json']) if data['complete_plan_json'] else None,
                    pdf_path=data['pdf_path'],
                    status=data['status'],
                    agents_completed=json.loads(data['agents_completed_json']) if data['agents_completed_json'] else [],
                    agents_failed=json.loads(data['agents_failed_json']) if data['agents_failed_json'] else [],
                    execution_start=datetime.fromisoformat(data['execution_start']) if data['execution_start'] else None,
                    execution_end=datetime.fromisoformat(data['execution_end']) if data['execution_end'] else None,
                    total_execution_seconds=data['total_execution_seconds'],
                    total_tokens_used=data['total_tokens_used'],
                    total_cost_estimate=data['total_cost_estimate'],
                    errors=json.loads(data['errors_json']) if data['errors_json'] else []
                )
                blackboards.append(blackboard)

            return blackboards

        finally:
            conn.close()


# Singleton instance
blackboard_service = BlackboardService()
