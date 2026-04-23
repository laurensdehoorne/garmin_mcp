"""
Activity Management functions for Garmin Connect MCP Server
"""
import json
import datetime
from typing import Any, Dict, List, Optional, Union

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all activity management tools with the MCP server app"""

    @app.tool()
    async def get_activities_by_date(start_date: str, end_date: str, activity_type: str = "") -> str:
        """Get activities data between specified dates, optionally filtered by activity type

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            activity_type: Optional activity type filter (e.g., cycling, running, swimming)
        """
        try:
            activities = garmin_client.get_activities_by_date(start_date, end_date, activity_type)
            if not activities:
                return f"No activities found between {start_date} and {end_date}" + \
                       (f" for activity type '{activity_type}'" if activity_type else "")

            # Curate the activity list
            curated = {
                "count": len(activities),
                "date_range": {"start": start_date, "end": end_date},
                "activities": []
            }

            for a in activities:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "max_hr_bpm": a.get('maxHR'),
                    "steps": a.get('steps'),
                }
                # Remove None values
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities by date: {str(e)}"

    @app.tool()
    async def get_activities_fordate(date: str) -> str:
        """Get activities for a specific date

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            data = garmin_client.get_activities_fordate(date)
            if not data:
                return f"No activities found for {date}"

            # Extract just the activities, not the embedded HR data
            activities_data = data.get('ActivitiesForDay', {})
            payload = activities_data.get('payload', [])

            if not payload:
                return f"No activities found for {date}"

            curated = {
                "date": date,
                "count": len(payload),
                "activities": []
            }

            for a in payload:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "steps": a.get('steps'),
                    "lap_count": a.get('lapCount'),
                    "moderate_intensity_minutes": a.get('moderateIntensityMinutes'),
                    "vigorous_intensity_minutes": a.get('vigorousIntensityMinutes'),
                }
                # Remove None values
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities for date: {str(e)}"

    @app.tool()
    async def get_activity(activity_id: int) -> str:
        """Get basic activity information

        Args:
            activity_id: ID of the activity to retrieve
        """
        try:
            activity = garmin_client.get_activity(activity_id)
            if not activity:
                return f"No activity found with ID {activity_id}"

            # Extract summary data
            summary = activity.get('summaryDTO', {})
            activity_type = activity.get('activityTypeDTO', {})
            metadata = activity.get('metadataDTO', {})

            curated = {
                "id": activity.get('activityId'),
                "name": activity.get('activityName'),
                "type": activity_type.get('typeKey'),
                "parent_type": activity_type.get('parentTypeId'),

                # Timing
                "start_time_local": summary.get('startTimeLocal'),
                "start_time_gmt": summary.get('startTimeGMT'),
                "duration_seconds": summary.get('duration'),
                "moving_duration_seconds": summary.get('movingDuration'),
                "elapsed_duration_seconds": summary.get('elapsedDuration'),

                # Distance and speed
                "distance_meters": summary.get('distance'),
                "avg_speed_mps": summary.get('averageSpeed'),
                "max_speed_mps": summary.get('maxSpeed'),

                # Heart rate
                "avg_hr_bpm": summary.get('averageHR'),
                "max_hr_bpm": summary.get('maxHR'),
                "min_hr_bpm": summary.get('minHR'),

                # Calories
                "calories": summary.get('calories'),
                "bmr_calories": summary.get('bmrCalories'),

                # Running metrics
                "avg_cadence": summary.get('averageRunCadence'),
                "max_cadence": summary.get('maxRunCadence'),
                "avg_stride_length_cm": summary.get('strideLength'),
                "avg_ground_contact_time_ms": summary.get('groundContactTime'),
                "avg_vertical_oscillation_cm": summary.get('verticalOscillation'),
                "steps": summary.get('steps'),

                # Power
                "avg_power_watts": summary.get('averagePower'),
                "max_power_watts": summary.get('maxPower'),
                "normalized_power_watts": summary.get('normalizedPower'),

                # Training effect
                "training_effect": summary.get('trainingEffect'),
                "anaerobic_training_effect": summary.get('anaerobicTrainingEffect'),
                "training_effect_label": summary.get('trainingEffectLabel'),
                "training_load": summary.get('activityTrainingLoad'),

                # Intensity minutes
                "moderate_intensity_minutes": summary.get('moderateIntensityMinutes'),
                "vigorous_intensity_minutes": summary.get('vigorousIntensityMinutes'),

                # Recovery
                "recovery_hr_bpm": summary.get('recoveryHeartRate'),
                "body_battery_impact": summary.get('differenceBodyBattery'),

                # Workout feedback
                "workout_feel": summary.get('directWorkoutFeel'),
                "workout_rpe": summary.get('directWorkoutRpe'),

                # Metadata
                "lap_count": metadata.get('lapCount'),
                "has_splits": metadata.get('hasSplits'),
                "device_manufacturer": metadata.get('manufacturer'),
            }

            # Remove None values
            curated = {k: v for k, v in curated.items() if v is not None}

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity: {str(e)}"

    @app.tool()
    async def get_activity_splits(activity_id: int) -> str:
        """Get splits for an activity

        Args:
            activity_id: ID of the activity to retrieve splits for
        """
        try:
            splits = garmin_client.get_activity_splits(activity_id)
            if not splits:
                return f"No splits found for activity with ID {activity_id}"

            # Curate the splits data
            laps = splits.get('lapDTOs', [])

            curated = {
                "activity_id": splits.get('activityId'),
                "lap_count": len(laps),
                "laps": []
            }

            for lap in laps:
                lap_data = {
                    "lap_number": lap.get('lapIndex'),
                    "start_time": lap.get('startTimeGMT'),
                    "distance_meters": lap.get('distance'),
                    "duration_seconds": lap.get('duration'),
                    "avg_speed_mps": lap.get('averageSpeed'),
                    "max_speed_mps": lap.get('maxSpeed'),
                    "avg_hr_bpm": lap.get('averageHR'),
                    "max_hr_bpm": lap.get('maxHR'),
                    "calories": lap.get('calories'),
                    "avg_cadence": lap.get('averageRunCadence'),
                    "avg_power_watts": lap.get('averagePower'),
                    "intensity_type": lap.get('intensityType'),
                    "elevation_gain_meters": lap.get('elevationGain'),
                    "elevation_loss_meters": lap.get('elevationLoss'),
                }
                # Remove None values
                lap_data = {k: v for k, v in lap_data.items() if v is not None}
                curated["laps"].append(lap_data)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity splits: {str(e)}"

    @app.tool()
    async def get_activity_typed_splits(activity_id: int) -> str:
        """Get typed splits for an activity

        Args:
            activity_id: ID of the activity to retrieve typed splits for
        """
        try:
            typed_splits = garmin_client.get_activity_typed_splits(activity_id)
            if not typed_splits:
                return f"No typed splits found for activity with ID {activity_id}"

            return json.dumps(typed_splits, indent=2)
        except Exception as e:
            return f"Error retrieving activity typed splits: {str(e)}"

    @app.tool()
    async def get_activity_split_summaries(activity_id: int) -> str:
        """Get split summaries for an activity

        Args:
            activity_id: ID of the activity to retrieve split summaries for
        """
        try:
            split_summaries = garmin_client.get_activity_split_summaries(activity_id)
            if not split_summaries:
                return f"No split summaries found for activity with ID {activity_id}"

            return json.dumps(split_summaries, indent=2)
        except Exception as e:
            return f"Error retrieving activity split summaries: {str(e)}"

    @app.tool()
    async def get_activity_weather(activity_id: int) -> str:
        """Get weather data for an activity

        Args:
            activity_id: ID of the activity to retrieve weather data for
        """
        try:
            weather = garmin_client.get_activity_weather(activity_id)
            if not weather:
                return f"No weather data found for activity with ID {activity_id}"

            # Curate weather data
            curated = {
                "activity_id": activity_id,
                "temperature_celsius": weather.get('temp'),
                "apparent_temperature_celsius": weather.get('apparentTemp'),
                "humidity_percent": weather.get('relativeHumidity'),
                "wind_speed_mps": weather.get('windSpeed'),
                "wind_direction_degrees": weather.get('windDirection'),
                "weather_type": weather.get('weatherTypeDTO', {}).get('weatherTypeName'),
                "weather_description": weather.get('weatherTypeDTO', {}).get('weatherTypeDesc'),
                "location": weather.get('issueLocation'),
                "issue_time": weather.get('issueDate'),
            }

            # Remove None values
            curated = {k: v for k, v in curated.items() if v is not None}

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity weather data: {str(e)}"

    @app.tool()
    async def get_activity_hr_in_timezones(activity_id: int) -> str:
        """Get heart rate data in different time zones for an activity

        Args:
            activity_id: ID of the activity to retrieve heart rate time zone data for
        """
        try:
            hr_zones = garmin_client.get_activity_hr_in_timezones(activity_id)
            if not hr_zones:
                return f"No heart rate time zone data found for activity with ID {activity_id}"

            return json.dumps(hr_zones, indent=2)
        except Exception as e:
            return f"Error retrieving activity heart rate time zone data: {str(e)}"

    @app.tool()
    async def get_activity_gear(activity_id: int) -> str:
        """Get gear data used for an activity

        Args:
            activity_id: ID of the activity to retrieve gear data for
        """
        try:
            gear = garmin_client.get_activity_gear(activity_id)
            if not gear:
                return f"No gear data found for activity with ID {activity_id}"

            return json.dumps(gear, indent=2)
        except Exception as e:
            return f"Error retrieving activity gear data: {str(e)}"

    @app.tool()
    async def get_activity_exercise_sets(activity_id: int) -> str:
        """Get exercise sets for strength training activities

        Args:
            activity_id: ID of the activity to retrieve exercise sets for
        """
        try:
            exercise_sets = garmin_client.get_activity_exercise_sets(activity_id)
            if not exercise_sets:
                return f"No exercise sets found for activity with ID {activity_id}"

            return json.dumps(exercise_sets, indent=2)
        except Exception as e:
            return f"Error retrieving activity exercise sets: {str(e)}"

    @app.tool()
    async def count_activities() -> str:
        """Get total count of activities in the user's Garmin account

        Returns the total number of activities recorded.
        """
        try:
            count = garmin_client.count_activities()
            if count is None:
                return "Unable to retrieve activity count"

            return json.dumps({
                "total_activities": count,
                "note": "Use get_activities() with pagination to retrieve activity details"
            }, indent=2)
        except Exception as e:
            return f"Error counting activities: {str(e)}"

    @app.tool()
    async def get_activities(start: int = 0, limit: int = 20) -> str:
        """Get activities with pagination support

        Retrieves a paginated list of activities. Use this for browsing through
        large activity lists more efficiently than get_activities_by_date.

        Args:
            start: Starting index (default 0, activities are ordered newest first)
            limit: Maximum number of activities to return (default 20, max 100)
        """
        try:
            # Cap limit at 100 for safety and performance
            limit = min(max(1, limit), 100)

            activities = garmin_client.get_activities(start, limit)
            if not activities:
                return f"No activities found at index {start}"

            # Curate the activity list
            curated = {
                "start": start,
                "limit": limit,
                "count": len(activities),
                "has_more": len(activities) == limit,
                "next_start": start + limit if len(activities) == limit else None,
                "activities": []
            }

            for a in activities:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "moving_duration_seconds": a.get('movingDuration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "max_hr_bpm": a.get('maxHR'),
                    "steps": a.get('steps'),
                    "owner_display_name": a.get('ownerDisplayName'),
                }
                # Remove None values
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities: {str(e)}"

    @app.tool()
    async def get_activity_types() -> str:
        """Get all available activity types

        Returns a list of all activity types supported by Garmin Connect,
        useful for filtering activities by type.
        """
        try:
            activity_types = garmin_client.get_activity_types()
            if not activity_types:
                return "No activity types found"

            # Curate the activity types list
            curated = {
                "count": len(activity_types),
                "activity_types": []
            }

            for at in activity_types:
                activity_type = {
                    "type_id": at.get('typeId'),
                    "type_key": at.get('typeKey'),
                    "display_name": at.get('displayName'),
                    "parent_type_id": at.get('parentTypeId'),
                    "is_hidden": at.get('isHidden'),
                }
                # Remove None values
                activity_type = {k: v for k, v in activity_type.items() if v is not None}
                curated["activity_types"].append(activity_type)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity types: {str(e)}"

    @app.tool()
    async def get_last_activity() -> str:
        """Get the most recent activity"""
        try:
            activities = garmin_client.get_activities(0, 1)
            if not activities:
                return "No activities found."

            activity = activities[0] if isinstance(activities, list) else None
            if not activity:
                return "No activities found."

            curated = {
                "id": activity.get('activityId'),
                "name": activity.get('activityName'),
                "type": activity.get('activityType', {}).get('typeKey'),
                "start_time": activity.get('startTimeLocal'),
                "distance_meters": activity.get('distance'),
                "duration_seconds": activity.get('duration'),
                "calories": activity.get('calories'),
                "avg_hr_bpm": activity.get('averageHR'),
                "max_hr_bpm": activity.get('maxHR'),
                "steps": activity.get('steps'),
            }
            curated = {k: v for k, v in curated.items() if v is not None}
            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving last activity: {str(e)}"

    @app.tool()
    async def get_activity_details(activity_id: int, max_chart: int = 2000, max_poly: int = 4000) -> str:
        """Get detailed time-series data for an activity (GPS, HR, pace, power over time)

        Note: Returns large dataset (~hundreds of KB). Use get_activity for a compact summary.

        Args:
            activity_id: ID of the activity
            max_chart: Max data points for charts (default 2000)
            max_poly: Max polyline points for GPS (default 4000, set 0 to skip)
        """
        try:
            details = garmin_client.get_activity_details(activity_id, maxchart=max_chart, maxpoly=max_poly)
            if not details:
                return f"No activity details found for ID {activity_id}"
            return json.dumps(details, indent=2)
        except Exception as e:
            return f"Error retrieving activity details: {str(e)}"

    @app.tool()
    async def get_activity_power_in_timezones(activity_id: int) -> str:
        """Get power time-in-zone distribution for an activity

        Args:
            activity_id: ID of the activity
        """
        try:
            data = garmin_client.get_activity_power_in_timezones(activity_id)
            if not data:
                return f"No power zone data found for activity {activity_id}"
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error retrieving power zone data: {str(e)}"

    @app.tool()
    async def set_activity_name(activity_id: int, name: str) -> str:
        """Rename an activity

        Args:
            activity_id: ID of the activity to rename
            name: New name for the activity
        """
        try:
            garmin_client.set_activity_name(str(activity_id), name)
            return json.dumps({
                "status": "success",
                "activity_id": activity_id,
                "new_name": name,
                "message": "Activity renamed successfully"
            }, indent=2)
        except Exception as e:
            return f"Error renaming activity: {str(e)}"

    @app.tool()
    async def set_activity_type(
        activity_id: int,
        type_id: int,
        type_key: str,
        parent_type_id: int
    ) -> str:
        """Change the type of an activity

        Use get_activity_types to find valid type_id, type_key, and parent_type_id values.

        Args:
            activity_id: ID of the activity to update
            type_id: Numeric activity type ID
            type_key: Activity type key (e.g., 'running', 'cycling')
            parent_type_id: Parent type ID from get_activity_types
        """
        try:
            garmin_client.set_activity_type(str(activity_id), type_id, type_key, parent_type_id)
            return json.dumps({
                "status": "success",
                "activity_id": activity_id,
                "new_type": type_key,
                "message": "Activity type updated successfully"
            }, indent=2)
        except Exception as e:
            return f"Error updating activity type: {str(e)}"

    @app.tool()
    async def create_manual_activity(
        start_datetime: str,
        time_zone: str,
        type_key: str,
        duration_min: int,
        distance_km: float = 0.0,
        activity_name: str = "Manual Activity"
    ) -> str:
        """Create a manual activity entry

        Logs a past activity that wasn't recorded by a device.

        Args:
            start_datetime: Start time in YYYY-MM-DDThh:mm:ss format (local time)
            time_zone: Timezone name (e.g., 'Europe/London', 'America/New_York')
            type_key: Activity type key (e.g., 'running', 'cycling', 'walking'). Use get_activity_types for valid values.
            duration_min: Duration in minutes
            distance_km: Distance in kilometers (default 0)
            activity_name: Name for the activity (default 'Manual Activity')
        """
        try:
            result = garmin_client.create_manual_activity(
                start_datetime=start_datetime,
                time_zone=time_zone,
                type_key=type_key,
                distance_km=distance_km,
                duration_min=duration_min,
                activity_name=activity_name,
            )
            if hasattr(result, 'json'):
                result = result.json()
            return json.dumps(result if result else {"status": "success", "message": "Activity created"}, indent=2)
        except Exception as e:
            return f"Error creating manual activity: {str(e)}"

    @app.tool()
    async def delete_activity(activity_id: int) -> str:
        """Permanently delete an activity

        Args:
            activity_id: ID of the activity to delete
        """
        try:
            garmin_client.delete_activity(str(activity_id))
            return json.dumps({
                "status": "success",
                "activity_id": activity_id,
                "message": f"Activity {activity_id} deleted successfully"
            }, indent=2)
        except Exception as e:
            return f"Error deleting activity: {str(e)}"

    @app.tool()
    async def download_activity(activity_id: int, format: str = "TCX") -> str:
        """Download an activity file

        Returns metadata about the downloaded bytes. The raw binary cannot be
        transmitted through MCP, but size and format are confirmed.

        Args:
            activity_id: ID of the activity to download
            format: File format - 'TCX', 'GPX', 'ORIGINAL' (FIT zip), 'KML', or 'CSV' (splits)
        """
        try:
            from garminconnect import Garmin
            format_map = {
                "TCX": Garmin.ActivityDownloadFormat.TCX,
                "GPX": Garmin.ActivityDownloadFormat.GPX,
                "ORIGINAL": Garmin.ActivityDownloadFormat.ORIGINAL,
                "KML": Garmin.ActivityDownloadFormat.KML,
                "CSV": Garmin.ActivityDownloadFormat.CSV,
            }
            dl_fmt = format_map.get(format.upper())
            if not dl_fmt:
                return f"Invalid format '{format}'. Valid options: TCX, GPX, ORIGINAL, KML, CSV"

            data = garmin_client.download_activity(str(activity_id), dl_fmt=dl_fmt)
            size = len(data) if isinstance(data, (bytes, bytearray)) else 0
            return json.dumps({
                "activity_id": activity_id,
                "format": format.upper(),
                "size_bytes": size,
                "message": f"Activity data available in {format.upper()} format ({size} bytes)"
            }, indent=2)
        except Exception as e:
            return f"Error downloading activity: {str(e)}"

    return app
