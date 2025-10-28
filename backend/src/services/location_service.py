"""Location validation and geocoding service."""

from typing import Optional

# NOTE: uszipcode has compatibility issues with Python 3.12 and SQLAlchemy 2.0
# For MVP, using simplified validation without external geocoding
# from uszipcode import SearchEngine

from ..utils.logger import setup_logger
from ..utils.validators import validate_zip_code

logger = setup_logger(__name__)


class LocationService:
    """Service for location validation and geocoding."""

    def __init__(self) -> None:
        """Initialize location service."""
        # self.search = SearchEngine()
        logger.info("LocationService initialized (simplified mode for MVP)")

    def validate_and_geocode(self, location_data: dict) -> Optional[dict]:
        """
        Validate location and add geocoding data.

        Args:
            location_data: Dict with 'zip_code' or 'city'+'state'

        Returns:
            Dict with validated location data including lat/long, or None if invalid
        """
        # Try ZIP code first
        if 'zip_code' in location_data and location_data['zip_code']:
            return self._geocode_zip(location_data['zip_code'])

        # Try city/state
        if 'city' in location_data and 'state' in location_data:
            return self._geocode_city_state(
                location_data['city'],
                location_data['state']
            )

        logger.warning("Location data missing required fields")
        return None

    def _geocode_zip(self, zip_code: str) -> Optional[dict]:
        """
        Geocode ZIP code (simplified for MVP).

        Args:
            zip_code: US ZIP code

        Returns:
            Location dict or None if invalid
        """
        if not validate_zip_code(zip_code):
            logger.warning(f"Invalid ZIP code format: {zip_code}")
            return None

        # For MVP: Accept ZIP without geocoding
        # In production, use uszipcode or external geocoding API
        location = {
            'zip_code': zip_code,
            'country': 'US',
            'latitude': None,
            'longitude': None
        }

        logger.info(f"Accepted ZIP {zip_code} (simplified validation)")
        return location

    def _geocode_city_state(self, city: str, state: str) -> Optional[dict]:
        """
        Geocode city and state (simplified for MVP).

        Args:
            city: City name
            state: State code (e.g., 'FL')

        Returns:
            Location dict or None if not found
        """
        # For MVP: Accept city/state without geocoding
        # In production, use uszipcode or external geocoding API
        location = {
            'city': city,
            'state': state,
            'country': 'US',
            'latitude': None,
            'longitude': None
        }

        logger.info(f"Accepted {city}, {state} (simplified validation)")
        return location

    def get_zip_info(self, zip_code: str) -> Optional[dict]:
        """
        Get detailed information about a ZIP code (simplified for MVP).

        Args:
            zip_code: US ZIP code

        Returns:
            Dict with ZIP info or None
        """
        if not validate_zip_code(zip_code):
            return None

        # For MVP: Return minimal info
        # In production, use uszipcode or external geocoding API
        return {
            'zipcode': zip_code,
            'city': None,
            'state': None,
            'county': None,
            'lat': None,
            'lng': None,
            'population': None,
            'density': None
        }
