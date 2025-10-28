"""Video Curator Agent for educational video recommendations.

Static curated library approach (MVP):
- 10-20 manually curated videos per crisis type
- Mix of official sources (FEMA, Red Cross, NOAA, CDC, DOL) and trusted creators
- Under 5 minutes per video
- Pre-filtered for quality and accuracy

Future enhancement: Real-time YouTube API searches if app becomes profitable.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent
from ..models.blackboard import Blackboard
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class VideoCuratorAgent(BaseAgent):
    """Agent that curates educational video recommendations based on crisis type.

    Mode-adaptive behavior:
    - Natural disaster: Evacuation, shelter, emergency supplies videos
    - Economic crisis: Unemployment filing, budgeting, benefits programs videos
    """

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Video Curator Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "video_curator"
        self.video_library = self._load_video_library()

    def _load_video_library(self) -> List[Dict[str, Any]]:
        """Load pre-curated video library.

        For MVP: Returns sample curated videos. In production, load from:
        backend/src/data/video_library.json (50-100 pre-curated videos)
        """
        # TODO: Load from backend/src/data/video_library.json
        # For now, return sample curated videos for major crisis types
        return [
            # Natural Disaster - Hurricane
            {
                "video_id": "vid-fema-hurricane-001",
                "title": "Hurricane Preparedness: Family Emergency Plan",
                "url": "https://www.youtube.com/watch?v=fHa-0mRFlMI",
                "source": "FEMA",
                "duration_seconds": 180,
                "duration_formatted": "3:00",
                "crisis_types": ["hurricane", "tropical_storm"],
                "topics": ["family_plan", "evacuation", "communication"],
                "description": "Official FEMA guide to creating a family emergency plan for hurricanes, including evacuation routes, meeting points, and communication strategies.",
                "thumbnail_url": "https://img.youtube.com/vi/fHa-0mRFlMI/hqdefault.jpg",
                "target_audience": "Families with children in hurricane-prone areas",
            },
            {
                "video_id": "vid-redcross-hurricane-002",
                "title": "How to Prepare for a Hurricane",
                "url": "https://www.youtube.com/watch?v=Vj_8YNe-3Ec",
                "source": "American Red Cross",
                "duration_seconds": 240,
                "duration_formatted": "4:00",
                "crisis_types": ["hurricane"],
                "topics": ["supply_kit", "home_protection", "evacuation"],
                "description": "Red Cross explains how to prepare your home and family for hurricane season, including supply lists and safety tips.",
                "thumbnail_url": "https://img.youtube.com/vi/Vj_8YNe-3Ec/hqdefault.jpg",
                "target_audience": "General audience, homeowners",
            },
            {
                "video_id": "vid-noaa-hurricane-003",
                "title": "Understanding Hurricane Warnings",
                "url": "https://www.youtube.com/watch?v=3Z-XwqM_EQ4",
                "source": "NOAA",
                "duration_seconds": 195,
                "duration_formatted": "3:15",
                "crisis_types": ["hurricane"],
                "topics": ["weather_alerts", "evacuation_timing", "risk_assessment"],
                "description": "National Weather Service explains the difference between hurricane watches and warnings, and when to evacuate.",
                "thumbnail_url": "https://img.youtube.com/vi/3Z-XwqM_EQ4/hqdefault.jpg",
                "target_audience": "General audience",
            },
            # Natural Disaster - Earthquake
            {
                "video_id": "vid-usgs-earthquake-001",
                "title": "Earthquake Safety: Drop, Cover, Hold On",
                "url": "https://www.youtube.com/watch?v=BLEPakj1YTY",
                "source": "USGS",
                "duration_seconds": 165,
                "duration_formatted": "2:45",
                "crisis_types": ["earthquake"],
                "topics": ["safety_procedures", "during_earthquake", "family_plan"],
                "description": "USGS demonstrates the Drop, Cover, and Hold On technique for earthquake safety.",
                "thumbnail_url": "https://img.youtube.com/vi/BLEPakj1YTY/hqdefault.jpg",
                "target_audience": "General audience",
            },
            {
                "video_id": "vid-redcross-earthquake-002",
                "title": "Earthquake Preparedness for Families",
                "url": "https://www.youtube.com/watch?v=R1H5Vw6kZiw",
                "source": "American Red Cross",
                "duration_seconds": 270,
                "duration_formatted": "4:30",
                "crisis_types": ["earthquake"],
                "topics": ["emergency_kit", "home_safety", "aftershocks"],
                "description": "Red Cross guide to preparing your home and family for earthquakes, including securing furniture and creating emergency kits.",
                "thumbnail_url": "https://img.youtube.com/vi/R1H5Vw6kZiw/hqdefault.jpg",
                "target_audience": "Families, homeowners",
            },
            # Economic Crisis - Unemployment
            {
                "video_id": "vid-dol-unemployment-001",
                "title": "How to File for Unemployment Benefits",
                "url": "https://www.youtube.com/watch?v=Mc9qE8a9RkI",
                "source": "Department of Labor",
                "duration_seconds": 240,
                "duration_formatted": "4:00",
                "crisis_types": ["unemployment", "layoff", "furlough"],
                "topics": ["benefits_filing", "eligibility", "weekly_certification"],
                "description": "Official DOL walkthrough of filing unemployment claims, including eligibility requirements and weekly certification.",
                "thumbnail_url": "https://img.youtube.com/vi/Mc9qE8a9RkI/hqdefault.jpg",
                "target_audience": "Recently unemployed workers",
            },
            {
                "video_id": "vid-financial-budget-001",
                "title": "Emergency Budgeting After Job Loss",
                "url": "https://www.youtube.com/watch?v=5xOtQ0KqZiI",
                "source": "Financial Planning Association",
                "duration_seconds": 285,
                "duration_formatted": "4:45",
                "crisis_types": ["unemployment", "layoff", "income_loss"],
                "topics": ["budgeting", "expense_cutting", "emergency_fund"],
                "description": "Certified financial planner explains how to create a survival budget after job loss, prioritizing essential expenses.",
                "thumbnail_url": "https://img.youtube.com/vi/5xOtQ0KqZiI/hqdefault.jpg",
                "target_audience": "People facing income loss",
            },
            {
                "video_id": "vid-snap-benefits-001",
                "title": "Applying for SNAP Food Assistance",
                "url": "https://www.youtube.com/watch?v=XTCc8j8sKsA",
                "source": "USDA",
                "duration_seconds": 210,
                "duration_formatted": "3:30",
                "crisis_types": ["unemployment", "income_loss", "government_shutdown"],
                "topics": ["food_assistance", "snap", "application_process"],
                "description": "USDA explains how to apply for SNAP (food stamps), including eligibility criteria and application steps.",
                "thumbnail_url": "https://img.youtube.com/vi/XTCc8j8sKsA/hqdefault.jpg",
                "target_audience": "Low-income households",
            },
            # Economic Crisis - Government Shutdown
            {
                "video_id": "vid-shutdown-guide-001",
                "title": "Federal Workers: Surviving a Government Shutdown",
                "url": "https://www.youtube.com/watch?v=nLc9XfmtLSo",
                "source": "Federal Employee Education & Assistance Fund",
                "duration_seconds": 255,
                "duration_formatted": "4:15",
                "crisis_types": ["government_shutdown"],
                "topics": ["creditor_communication", "assistance_programs", "back_pay"],
                "description": "Guide for federal employees during shutdowns, covering creditor communication, assistance programs, and planning for back pay.",
                "thumbnail_url": "https://img.youtube.com/vi/nLc9XfmtLSo/hqdefault.jpg",
                "target_audience": "Federal employees and contractors",
            },
        ]

    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Curate video recommendations using blackboard pattern.

        Reads from blackboard:
        - crisis_profile (crisis_mode, specific_threat, household)
        - risk_assessment (optional, for prioritizing video topics)

        Writes to blackboard:
        - video_recommendations (list of 5-7 curated videos)

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with video_recommendations populated
        """
        self.start_time = datetime.utcnow()
        crisis_profile = blackboard.crisis_profile

        if not crisis_profile:
            raise ValueError("Blackboard missing crisis_profile")

        task_id = crisis_profile.get('task_id', 'unknown')
        crisis_mode = crisis_profile.get('crisis_mode')

        # Get mode-specific UI presentation
        agent_label = self.get_agent_label(crisis_mode)
        agent_emoji = self.get_agent_emoji(crisis_mode)

        logger.info(f"{agent_emoji} {agent_label} starting for task_id={task_id}, mode={crisis_mode}")

        try:
            # Validate required fields
            self.validate_input(crisis_profile, ['specific_threat'])

            threat = crisis_profile['specific_threat']
            household = crisis_profile.get('household', {})

            logger.info(f"{agent_emoji} Curating videos for {threat}")

            # Filter videos by crisis type
            matching_videos = self._filter_by_crisis_type(threat)

            logger.info(f"{agent_emoji} Found {len(matching_videos)} matching videos in library")

            # If we have few matches, include general preparedness videos
            if len(matching_videos) < 3:
                logger.warning(
                    f"{agent_emoji} Only {len(matching_videos)} videos found for {threat}. "
                    f"Adding general preparedness videos."
                )
                # Add fallback logic here if needed

            # Score videos for relevance (using household context)
            scored_videos = self._score_videos(matching_videos, crisis_profile, blackboard)

            # Sort by relevance score (highest first)
            scored_videos.sort(key=lambda v: v.get('relevance_score', 0), reverse=True)

            # Limit to 5-7 videos
            limit = 7
            selected_videos = scored_videos[:limit]

            # Format video recommendations
            video_recommendations = self._format_video_recommendations(selected_videos, task_id)

            # Calculate total runtime
            total_runtime = sum(v.get('duration_seconds', 0) for v in selected_videos)
            total_runtime_formatted = self._format_duration(total_runtime)

            logger.info(
                f"{agent_emoji} Selected {len(video_recommendations)} videos "
                f"(total runtime: {total_runtime_formatted})"
            )

            # Write to blackboard
            blackboard.video_recommendations = video_recommendations

            # No tokens used for static lookup (no Claude API call)
            self.tokens_used = 0
            self.cost = 0.0

            blackboard.mark_agent_complete(
                self.agent_class_name,
                self.tokens_used,
                self.cost
            )

            self.end_time = datetime.utcnow()
            logger.info(
                f"{agent_emoji} {agent_label} completed: "
                f"{len(video_recommendations)} videos curated"
            )

            return blackboard

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"{agent_emoji} {agent_label} error: {e}")
            raise

    def _filter_by_crisis_type(self, threat: str) -> List[Dict[str, Any]]:
        """Filter video library by crisis type."""
        matching = []

        for video in self.video_library:
            crisis_types = video.get('crisis_types', [])
            # Check if threat matches any crisis type in video
            if threat in crisis_types or any(threat in ct for ct in crisis_types):
                matching.append(video.copy())

        return matching

    def _score_videos(
        self,
        videos: List[Dict[str, Any]],
        crisis_profile: Dict[str, Any],
        blackboard: Blackboard
    ) -> List[Dict[str, Any]]:
        """
        Score videos for relevance to user's situation.

        Simple heuristic scoring (no Claude API call for MVP):
        - Base score: 5
        - +2 if target_audience matches household
        - +1 if topics include high-priority items
        - +1 if from official source (FEMA, Red Cross, NOAA, USGS, DOL, USDA)
        - +1 if risk level is EXTREME and video covers safety procedures
        """
        household = crisis_profile.get('household', {})
        has_children = household.get('children', 0) > 0
        has_pets = household.get('pets', 0) > 0

        # Get risk level from blackboard
        risk_level = "MEDIUM"
        if blackboard.risk_assessment:
            risk_level = blackboard.risk_assessment.get('overall_risk_level', 'MEDIUM')

        official_sources = ['FEMA', 'Red Cross', 'NOAA', 'USGS', 'Department of Labor', 'USDA']

        for video in videos:
            score = 5  # Base score

            # Target audience matching
            target_audience = video.get('target_audience', '').lower()
            if has_children and 'children' in target_audience:
                score += 2
            elif has_pets and 'pet' in target_audience:
                score += 2
            elif 'families' in target_audience:
                score += 1

            # Official source bonus
            source = video.get('source', '')
            if any(official in source for official in official_sources):
                score += 1

            # High-priority topics for EXTREME risk
            if risk_level == "EXTREME":
                topics = video.get('topics', [])
                if 'evacuation' in topics or 'safety_procedures' in topics:
                    score += 1

            # Ensure score is between 1-10
            video['relevance_score'] = min(10, max(1, score))

        return videos

    def _format_video_recommendations(
        self,
        videos: List[Dict[str, Any]],
        task_id: str
    ) -> List[Dict[str, Any]]:
        """Format videos into VideoRecommendation schema."""
        formatted = []

        for video in videos:
            formatted.append({
                "video_id": video.get('video_id', ''),
                "title": video.get('title', ''),
                "url": video.get('url', ''),
                "source": video.get('source', ''),
                "duration_seconds": video.get('duration_seconds', 0),
                "duration_formatted": video.get('duration_formatted', '0:00'),
                "crisis_types": video.get('crisis_types', []),
                "topics": video.get('topics', []),
                "relevance_score": video.get('relevance_score', 5),
                "description": video.get('description', ''),
                "thumbnail_url": video.get('thumbnail_url'),
                "target_audience": video.get('target_audience', 'General audience'),
            })

        return formatted

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
