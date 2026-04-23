"""
Golf functions for Garmin Connect MCP Server
"""
import json
from typing import Any, Dict, List, Optional, Union

garmin_client = None


def configure(client):
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all golf tools with the MCP server app"""

    @app.tool()
    async def get_golf_summary(start: int = 0, limit: int = 20) -> str:
        """Get golf scorecard summaries

        Args:
            start: Starting offset for pagination (default 0)
            limit: Maximum number of scorecards to return (default 20, max 100)
        """
        try:
            limit = min(max(1, limit), 100)
            data = garmin_client.get_golf_summary(start=start, limit=limit)
            if not data:
                return "No golf scorecards found."
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error retrieving golf summary: {str(e)}"

    @app.tool()
    async def get_golf_scorecard(scorecard_id: int) -> str:
        """Get detailed golf scorecard for a specific round

        Args:
            scorecard_id: The scorecard ID (get from get_golf_summary)
        """
        try:
            data = garmin_client.get_golf_scorecard(scorecard_id)
            if not data:
                return f"No golf scorecard found with ID {scorecard_id}"
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error retrieving golf scorecard: {str(e)}"

    @app.tool()
    async def get_golf_shot_data(scorecard_id: int, hole_numbers: str = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18") -> str:
        """Get shot-by-shot data for a golf round

        Args:
            scorecard_id: The scorecard ID (get from get_golf_summary)
            hole_numbers: Comma-separated hole numbers to retrieve (default: all 18)
        """
        try:
            data = garmin_client.get_golf_shot_data(scorecard_id, hole_numbers=hole_numbers)
            if not data:
                return f"No shot data found for scorecard {scorecard_id}"
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error retrieving golf shot data: {str(e)}"

    return app
