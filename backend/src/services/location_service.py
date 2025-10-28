"""Location validation and geocoding service."""

from typing import Optional

from uszipcode import SearchEngine

from ..utils.logger import setup_logger
from ..utils.validators import validate_zip_code

logger = setup_logger(__name__)


class LocationService:
    """Service for location validation and geocoding."""

    def __init__(self) -> None:
        """Initialize location service with uszipcode."""
        self.search = SearchEngine()

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
        Geocode ZIP code.

        Args:
            zip_code: US ZIP code

        Returns:
            Location dict or None if invalid
        """
        if not validate_zip_code(zip_code):
            logger.warning(f"Invalid ZIP code format: {zip_code}")
            return None

        try:
            result = self.search.by_zipcode(zip_code)

            if not result or not result.major_city:
                logger.warning(f"ZIP code not found: {zip_code}")
                return None

            location = {
                'zip_code': result.zipcode,
                'city': result.major_city,
                'state': result.state,
                'country': 'US',
                'latitude': result.lat,
                'longitude': result.lng
            }

            logger.info(f"Geocoded ZIP {zip_code}: {location['city']}, {location['state']}")
            return location

        except Exception as e:
            logger.error(f"Geocoding error for ZIP {zip_code}: {e}")
            return None

    def _geocode_city_state(self, city: str, state: str) -> Optional[dict]:
        """
        Geocode city and state.

        Args:
            city: City name
            state: State code (e.g., 'FL')

        Returns:
            Location dict or None if not found
        """
        try:
            # Search by city and state
            results = self.search.by_city_and_state(city, state)

            if not results or len(results) == 0:
                logger.warning(f"City/state not found: {city}, {state}")
                return None

            # Use first result
            result = results[0]

            location = {
                'city': result.major_city or city,
                'state': result.state,
                'country': 'US',
                'latitude': result.lat,
                'longitude': result.lng
            }

            # Add ZIP if available
            if result.zipcode:
                location['zip_code'] = result.zipcode

            logger.info(f"Geocoded {city}, {state}: {location}")
            return location

        except Exception as e:
            logger.error(f"Geocoding error for {city}, {state}: {e}")
            return None

    def get_zip_info(self, zip_code: str) -> Optional[dict]:
        """
        Get detailed information about a ZIP code.

        Args:
            zip_code: US ZIP code

        Returns:
            Dict with ZIP info or None
        """
        if not validate_zip_code(zip_code):
            return None

        try:
            result = self.search.by_zipcode(zip_code)

            if not result:
                return None

            return {
                'zipcode': result.zipcode,
                'city': result.major_city,
                'state': result.state,
                'county': result.county,
                'lat': result.lat,
                'lng': result.lng,
                'population': result.population,
                'density': result.population_density
            }

        except Exception as e:
            logger.error(f"Error getting ZIP info for {zip_code}: {e}")
            return None
