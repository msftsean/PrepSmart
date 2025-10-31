"""Resource Locator Agent for finding local assistance resources.

Hybrid approach:
- Primary: Static database of pre-vetted resources (faster, more reliable)
- Fallback: Google Places API (if static database has insufficient results)

For MVP: Focus on static database with mode-specific resource types.
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent
from ..models.blackboard import Blackboard
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ResourceLocatorAgent(BaseAgent):
    """Agent that finds local assistance resources based on crisis type and location.

    Mode-adaptive behavior:
    - Natural disaster: Shelters, hospitals, emergency services
    - Economic crisis: Food banks, unemployment offices, legal aid
    """

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Resource Locator Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "resource_locator"
        self.static_resources = self._load_static_resources()

    def _load_static_resources(self) -> List[Dict[str, Any]]:
        """Load pre-vetted resources from static database.

        For MVP: Returns sample resources. In production, load from:
        backend/src/data/resources.json (200+ pre-vetted resources)
        """
        # TODO: Load from backend/src/data/resources.json
        # For now, return sample resources for major cities
        return [
            # Miami, FL - Hurricane/Natural Disaster
            {
                "resource_id": "shelter-fl-miami-001",
                "name": "Miami Beach Community Center Emergency Shelter",
                "resource_type": "shelter",
                "address": "2100 Washington Ave",
                "city": "Miami Beach",
                "state": "FL",
                "zip_code": "33139",
                "latitude": 25.7959,
                "longitude": -80.1396,
                "phone": "(305) 673-7730",
                "website": "https://www.miamibeachfl.gov",
                "hours_of_operation": "Opens when emergency declared",
                "services_offered": ["Emergency shelter", "Cots and blankets", "Meals (limited)"],
                "data_source": "FEMA Shelter Directory",
            },
            {
                "resource_id": "hospital-fl-miami-001",
                "name": "Jackson Memorial Hospital",
                "resource_type": "hospital",
                "address": "1611 NW 12th Ave",
                "city": "Miami",
                "state": "FL",
                "zip_code": "33136",
                "latitude": 25.7894,
                "longitude": -80.2100,
                "phone": "(305) 585-1111",
                "website": "https://jacksonhealth.org",
                "hours_of_operation": "24/7",
                "services_offered": ["Emergency care", "Trauma center", "Critical care"],
                "data_source": "Hospital Directory",
            },
            {
                "resource_id": "foodbank-fl-miami-001",
                "name": "Feeding South Florida",
                "resource_type": "food_bank",
                "address": "2501 SW 32nd Terrace",
                "city": "Pembroke Park",
                "state": "FL",
                "zip_code": "33023",
                "latitude": 25.9881,
                "longitude": -80.1739,
                "phone": "(954) 518-1818",
                "website": "https://feedingsouthflorida.org",
                "hours_of_operation": "Mon-Fri 8am-4pm",
                "services_offered": ["Food distribution", "SNAP enrollment", "Nutrition education"],
                "data_source": "Feeding America Network",
            },
            # Austin, TX - Economic Crisis
            {
                "resource_id": "unemployment-tx-austin-001",
                "name": "Texas Workforce Commission - Austin",
                "resource_type": "unemployment_office",
                "address": "6705 Hwy 290 E",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78723",
                "latitude": 30.2967,
                "longitude": -97.6781,
                "phone": "1-800-939-6631",
                "website": "https://www.twc.texas.gov",
                "hours_of_operation": "Mon-Fri 8am-5pm",
                "services_offered": ["Unemployment claims", "Job search assistance", "Career counseling"],
                "data_source": "State Government Directory",
            },
            {
                "resource_id": "foodbank-tx-austin-001",
                "name": "Central Texas Food Bank",
                "resource_type": "food_bank",
                "address": "6500 Metropolis Dr",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78744",
                "latitude": 30.1933,
                "longitude": -97.7481,
                "phone": "(512) 684-2550",
                "website": "https://centraltexasfoodbank.org",
                "hours_of_operation": "Mon-Fri 8am-5pm",
                "services_offered": ["Food pantry", "Mobile food distributions", "SNAP assistance"],
                "data_source": "Feeding America Network",
            },
            {
                "resource_id": "legal-tx-austin-001",
                "name": "Texas RioGrande Legal Aid",
                "resource_type": "legal_aid",
                "address": "4920 N IH 35",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78751",
                "latitude": 30.3159,
                "longitude": -97.7228,
                "phone": "(512) 374-2700",
                "website": "https://www.trla.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Eviction defense", "Consumer protection", "Public benefits advocacy"],
                "eligibility_requirements": "Low-income households",
                "data_source": "Legal Services Corporation",
            },

            # Washington, DC - Economic Crisis / Natural Disaster
            {
                "resource_id": "foodbank-dc-001",
                "name": "Capital Area Food Bank",
                "resource_type": "food_bank",
                "address": "4900 Puerto Rico Ave NE",
                "city": "Washington",
                "state": "DC",
                "zip_code": "20017",
                "latitude": 38.9290,
                "longitude": -76.9946,
                "phone": "(202) 644-9800",
                "website": "https://www.capitalareafoodbank.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Food pantry", "Mobile markets", "SNAP outreach", "Nutrition education"],
                "data_source": "Feeding America Network",
            },
            {
                "resource_id": "unemployment-dc-001",
                "name": "DC Department of Employment Services",
                "resource_type": "unemployment_office",
                "address": "4058 Minnesota Ave NE",
                "city": "Washington",
                "state": "DC",
                "zip_code": "20019",
                "latitude": 38.8997,
                "longitude": -76.9467,
                "phone": "(202) 724-7000",
                "website": "https://does.dc.gov",
                "hours_of_operation": "Mon-Fri 8:30am-4:30pm",
                "services_offered": ["Unemployment claims", "Job search assistance", "Career counseling", "Re-employment services"],
                "data_source": "DC Government",
            },
            {
                "resource_id": "legal-dc-001",
                "name": "Legal Aid Society of DC",
                "resource_type": "legal_aid",
                "address": "1331 H St NW #350",
                "city": "Washington",
                "state": "DC",
                "zip_code": "20005",
                "latitude": 38.9003,
                "longitude": -77.0297,
                "phone": "(202) 628-1161",
                "website": "https://www.legalaiddc.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Eviction prevention", "Public benefits appeals", "Consumer law", "Domestic violence"],
                "eligibility_requirements": "Low-income DC residents",
                "data_source": "Legal Services Corporation",
            },
            {
                "resource_id": "shelter-dc-001",
                "name": "Washington Convention Center - Emergency Shelter",
                "resource_type": "shelter",
                "address": "801 Mount Vernon Pl NW",
                "city": "Washington",
                "state": "DC",
                "zip_code": "20001",
                "latitude": 38.9050,
                "longitude": -77.0227,
                "phone": "(202) 249-3000",
                "website": "https://www.dcconvention.com",
                "hours_of_operation": "Opens when emergency declared",
                "services_offered": ["Emergency shelter", "Cots and blankets", "Meals (limited)", "Red Cross services"],
                "data_source": "DC Emergency Management",
            },

            # New York City, NY - Economic Crisis / Natural Disaster (DEFAULT FALLBACK)
            {
                "resource_id": "foodbank-ny-nyc-001",
                "name": "City Harvest",
                "resource_type": "food_bank",
                "address": "150 52nd St",
                "city": "Brooklyn",
                "state": "NY",
                "zip_code": "11232",
                "latitude": 40.6533,
                "longitude": -74.0112,
                "phone": "(917) 351-8700",
                "website": "https://www.cityharvest.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Food pantry", "Mobile markets", "SNAP enrollment", "Nutrition education"],
                "data_source": "Feeding America Network",
            },
            {
                "resource_id": "unemployment-ny-nyc-001",
                "name": "NYC Department of Labor Career Center",
                "resource_type": "unemployment_office",
                "address": "168-46 91st Ave",
                "city": "Jamaica",
                "state": "NY",
                "zip_code": "11432",
                "latitude": 40.7052,
                "longitude": -73.7937,
                "phone": "1-888-209-8124",
                "website": "https://dol.ny.gov",
                "hours_of_operation": "Mon-Fri 8am-5pm",
                "services_offered": ["Unemployment claims", "Job placement", "Resume help", "Career training"],
                "data_source": "NY State Department of Labor",
            },
            {
                "resource_id": "legal-ny-nyc-001",
                "name": "Legal Aid Society",
                "resource_type": "legal_aid",
                "address": "199 Water St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10038",
                "latitude": 40.7089,
                "longitude": -74.0062,
                "phone": "(212) 577-3300",
                "website": "https://www.legalaidnyc.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Eviction defense", "Public benefits", "Family law", "Consumer rights"],
                "eligibility_requirements": "Low-income NYC residents",
                "data_source": "Legal Services Corporation",
            },
            {
                "resource_id": "shelter-ny-nyc-001",
                "name": "Jacob K. Javits Convention Center - Emergency Shelter",
                "resource_type": "shelter",
                "address": "429 11th Ave",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "latitude": 40.7559,
                "longitude": -74.0024,
                "phone": "(212) 216-2000",
                "website": "https://www.javitscenter.com",
                "hours_of_operation": "Opens when emergency declared",
                "services_offered": ["Emergency shelter", "Medical services", "Meals", "Family reunification"],
                "data_source": "NYC Emergency Management",
            },

            # Miami, FL - Economic Crisis (additional resources)
            {
                "resource_id": "unemployment-fl-miami-001",
                "name": "CareerSource South Florida",
                "resource_type": "unemployment_office",
                "address": "7300 Corporate Center Dr #400",
                "city": "Miami",
                "state": "FL",
                "zip_code": "33126",
                "latitude": 25.7859,
                "longitude": -80.3167,
                "phone": "(305) 594-7615",
                "website": "https://careersourcesfl.com",
                "hours_of_operation": "Mon-Fri 8am-5pm",
                "services_offered": ["Unemployment assistance", "Job search", "Skills training", "Veterans services"],
                "data_source": "Florida Department of Economic Opportunity",
            },
            {
                "resource_id": "legal-fl-miami-001",
                "name": "Legal Services of Greater Miami",
                "resource_type": "legal_aid",
                "address": "3000 Biscayne Blvd #500",
                "city": "Miami",
                "state": "FL",
                "zip_code": "33137",
                "latitude": 25.8055,
                "longitude": -80.1878,
                "phone": "(305) 576-0080",
                "website": "https://www.legalservicesmiami.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Housing assistance", "Consumer law", "Family law", "Immigration"],
                "eligibility_requirements": "Low-income residents",
                "data_source": "Legal Services Corporation",
            },

            # Los Angeles, CA - Economic Crisis / Natural Disaster
            {
                "resource_id": "foodbank-ca-la-001",
                "name": "Los Angeles Regional Food Bank",
                "resource_type": "food_bank",
                "address": "1734 E 41st St",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90058",
                "latitude": 34.0098,
                "longitude": -118.2436,
                "phone": "(323) 234-3030",
                "website": "https://www.lafoodbank.org",
                "hours_of_operation": "Mon-Fri 8am-4:30pm",
                "services_offered": ["Food distribution", "Mobile pantries", "CalFresh enrollment", "Nutrition classes"],
                "data_source": "Feeding America Network",
            },
            {
                "resource_id": "unemployment-ca-la-001",
                "name": "LA County Workforce Development Center",
                "resource_type": "unemployment_office",
                "address": "3580 Wilshire Blvd #400",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90010",
                "latitude": 34.0616,
                "longitude": -118.3092,
                "phone": "1-800-300-5616",
                "website": "https://edd.ca.gov",
                "hours_of_operation": "Mon-Fri 8am-5pm",
                "services_offered": ["Unemployment insurance", "Job search", "Training programs", "Disability insurance"],
                "data_source": "CA Employment Development Department",
            },
            {
                "resource_id": "legal-ca-la-001",
                "name": "Legal Aid Foundation of Los Angeles",
                "resource_type": "legal_aid",
                "address": "1102 Crenshaw Blvd",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90019",
                "latitude": 34.0515,
                "longitude": -118.3352,
                "phone": "(800) 399-4529",
                "website": "https://www.lafla.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Eviction defense", "Public benefits", "Domestic violence", "Consumer protection"],
                "eligibility_requirements": "Low-income LA County residents",
                "data_source": "Legal Services Corporation",
            },
            {
                "resource_id": "shelter-ca-la-001",
                "name": "LA Convention Center - Emergency Operations",
                "resource_type": "shelter",
                "address": "1201 S Figueroa St",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90015",
                "latitude": 34.0407,
                "longitude": -118.2697,
                "phone": "(213) 741-1151",
                "website": "https://www.lacclink.com",
                "hours_of_operation": "Opens during emergencies",
                "services_offered": ["Emergency shelter", "Medical triage", "Disaster relief", "Red Cross coordination"],
                "data_source": "LA Emergency Management",
            },

            # San Francisco, CA - Economic Crisis / Natural Disaster
            {
                "resource_id": "foodbank-ca-sf-001",
                "name": "SF-Marin Food Bank",
                "resource_type": "food_bank",
                "address": "900 Pennsylvania Ave",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94107",
                "latitude": 37.7518,
                "longitude": -122.3965,
                "phone": "(415) 282-1900",
                "website": "https://www.sfmfoodbank.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Food pantries", "Home delivery", "CalFresh assistance", "Nutrition workshops"],
                "data_source": "Feeding America Network",
            },
            {
                "resource_id": "unemployment-ca-sf-001",
                "name": "SF Workforce Development Center",
                "resource_type": "unemployment_office",
                "address": "1390 Market St #200",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "latitude": 37.7767,
                "longitude": -122.4174,
                "phone": "1-800-300-5616",
                "website": "https://oewd.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Unemployment claims", "Career counseling", "Job training", "Small business support"],
                "data_source": "SF Office of Economic & Workforce Development",
            },
            {
                "resource_id": "legal-ca-sf-001",
                "name": "Bay Area Legal Aid",
                "resource_type": "legal_aid",
                "address": "1735 Telegraph Ave",
                "city": "Oakland",
                "state": "CA",
                "zip_code": "94612",
                "latitude": 37.8078,
                "longitude": -122.2690,
                "phone": "(800) 551-5554",
                "website": "https://baylegal.org",
                "hours_of_operation": "Mon-Fri 9am-5pm",
                "services_offered": ["Housing rights", "Public benefits", "Healthcare access", "Consumer law"],
                "eligibility_requirements": "Low-income Bay Area residents",
                "data_source": "Legal Services Corporation",
            },
            {
                "resource_id": "shelter-ca-sf-001",
                "name": "Moscone Convention Center - Emergency Shelter",
                "resource_type": "shelter",
                "address": "747 Howard St",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94103",
                "latitude": 37.7841,
                "longitude": -122.4014,
                "phone": "(415) 974-4000",
                "website": "https://www.moscone.com",
                "hours_of_operation": "Opens when emergency declared",
                "services_offered": ["Emergency shelter", "Medical support", "Food services", "Pet-friendly areas"],
                "data_source": "SF Department of Emergency Management",
            },
        ]

    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Find local assistance resources using blackboard pattern.

        Reads from blackboard:
        - crisis_profile (crisis_mode, specific_threat, location)
        - risk_assessment (optional, for prioritizing resource types)

        Writes to blackboard:
        - resource_locations (list of nearby resources sorted by distance)

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with resource_locations populated
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
            self.validate_input(crisis_profile, ['location'])

            location = crisis_profile['location']
            city = location.get('city', '')
            state = location.get('state', '')
            latitude = location.get('latitude')
            longitude = location.get('longitude')

            logger.info(
                f"{agent_emoji} Finding resources near {city}, {state} "
                f"(lat={latitude}, lon={longitude})"
            )

            # Determine resource types based on crisis mode
            if crisis_mode == "natural_disaster":
                resource_types = ["shelter", "hospital", "community_center"]
            elif crisis_mode == "economic_crisis":
                resource_types = ["food_bank", "unemployment_office", "legal_aid"]
            else:
                resource_types = ["shelter", "food_bank", "hospital"]

            # Find resources from static database
            resources = self._find_resources_static(
                city=city,
                state=state,
                latitude=latitude,
                longitude=longitude,
                resource_types=resource_types,
                max_distance_miles=50,
                limit=10
            )

            logger.info(f"{agent_emoji} Found {len(resources)} resources in static database")

            # If insufficient results, could fallback to API here
            # For MVP, we're using static database only
            if len(resources) < 3:
                logger.warning(
                    f"{agent_emoji} Only {len(resources)} resources found. "
                    f"Consider expanding search radius or using API fallback."
                )

            # Format resource locations
            resource_locations = self._format_resource_locations(resources, task_id)

            # Write to blackboard
            blackboard.resource_locations = resource_locations

            # No tokens used for static lookup (no Claude API call)
            self.tokens_used = 0
            self.cost = 0.0

            blackboard.mark_agent_complete(
                self.agent_class_name,
                self.tokens_used,
                self.cost
            )

            self.end_time = datetime.utcnow()

            # Log completion for UI
            self.log_activity(
                task_id,
                "completed",
                "Resource search complete",
                100
            )

            logger.info(
                f"{agent_emoji} {agent_label} completed: "
                f"{len(resource_locations)} resources found"
            )

            # Log comprehensive debug output
            self.log_agent_output(task_id, resource_locations, agent_emoji)

            return blackboard

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"{agent_emoji} {agent_label} error: {e}")
            raise

    def _find_resources_static(
        self,
        city: str,
        state: str,
        latitude: Optional[float],
        longitude: Optional[float],
        resource_types: List[str],
        max_distance_miles: float = 50,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find resources from static database.

        Args:
            city: User's city
            state: User's state (2-letter code)
            latitude: User's latitude (for distance calculation)
            longitude: User's longitude (for distance calculation)
            resource_types: List of resource types to include
            max_distance_miles: Maximum distance to include
            limit: Maximum number of results

        Returns:
            List of resources sorted by distance
        """
        # Filter by resource type
        filtered = [
            r for r in self.static_resources
            if r.get('resource_type') in resource_types
        ]

        # Filter by state (same state or nearby states)
        filtered = [
            r for r in filtered
            if r.get('state') == state or self._is_nearby_state(state, r.get('state'))
        ]

        # Calculate distances
        if latitude is not None and longitude is not None:
            for resource in filtered:
                res_lat = resource.get('latitude')
                res_lon = resource.get('longitude')
                if res_lat is not None and res_lon is not None:
                    distance = self._calculate_distance(
                        latitude, longitude, res_lat, res_lon
                    )
                    resource['distance_miles'] = round(distance, 1)
                else:
                    resource['distance_miles'] = None

            # Filter by max distance (but keep resources with distance even if beyond max)
            filtered_with_distance = [
                r for r in filtered
                if r.get('distance_miles') is not None and r['distance_miles'] <= max_distance_miles
            ]

            # If we got results within distance, use them; otherwise use all in-state resources
            if len(filtered_with_distance) > 0:
                filtered = filtered_with_distance
                # Sort by distance
                filtered.sort(key=lambda r: r.get('distance_miles', float('inf')))
            else:
                # No resources within max_distance, so return in-state resources without distance filtering
                logger.warning(
                    f"No resources within {max_distance_miles} miles. "
                    f"Returning {len(filtered)} in-state resources."
                )
        else:
            # No coordinates provided, return in-state resources
            logger.info(f"No coordinates provided. Returning {len(filtered)} in-state resources.")

        # Fallback to NYC resources if no results found
        if len(filtered) == 0:
            logger.warning(f"No resources found for {city}, {state}. Falling back to NYC resources.")
            # Get NYC resources as fallback
            nyc_resources = [
                r for r in self.static_resources
                if r.get('state') == 'NY' and r.get('resource_type') in resource_types
            ]
            # Remove distance info since it's not accurate for fallback
            for resource in nyc_resources:
                resource['distance_miles'] = None
                resource['note'] = "National resource - contact for assistance in your area"
            filtered = nyc_resources

        # Limit results
        return filtered[:limit]

    def _is_nearby_state(self, user_state: str, resource_state: str) -> bool:
        """Check if resource state is nearby to user state."""
        # For MVP: Simple adjacent state checking
        # TODO: Implement comprehensive state adjacency matrix
        adjacent_states = {
            'FL': ['GA', 'AL'],
            'TX': ['OK', 'LA', 'AR', 'NM'],
            'CA': ['OR', 'NV', 'AZ'],
            # Add more as needed
        }
        return resource_state in adjacent_states.get(user_state, [])

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two lat/lon points using Haversine formula.

        Args:
            lat1: User latitude
            lon1: User longitude
            lat2: Resource latitude
            lon2: Resource longitude

        Returns:
            Distance in miles
        """
        # Radius of Earth in miles
        R = 3959.0

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def _format_resource_locations(
        self,
        resources: List[Dict[str, Any]],
        task_id: str
    ) -> List[Dict[str, Any]]:
        """Format resources into ResourceLocation schema."""
        formatted = []

        for resource in resources:
            formatted.append({
                "resource_id": resource.get('resource_id', ''),
                "name": resource.get('name', ''),
                "resource_type": resource.get('resource_type', ''),
                "address": resource.get('address', ''),
                "city": resource.get('city', ''),
                "state": resource.get('state', ''),
                "zip_code": resource.get('zip_code', ''),
                "latitude": resource.get('latitude'),
                "longitude": resource.get('longitude'),
                "phone": resource.get('phone'),
                "website": resource.get('website'),
                "email": resource.get('email'),
                "hours_of_operation": resource.get('hours_of_operation'),
                "services_offered": resource.get('services_offered', []),
                "eligibility_requirements": resource.get('eligibility_requirements'),
                "distance_miles": resource.get('distance_miles'),
                "data_source": resource.get('data_source', 'Static Database'),
                "last_verified": resource.get('last_verified'),
            })

        return formatted
