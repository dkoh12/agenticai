from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initiailize FastMCP server for weather data
mcp = FastMCP("weather")

# Constants
NWS_API_URL = "https://api.weather.gov/"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the National Weather Service API."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
    return None

def format_alert(feature: dict) -> str:
    """Format a weather alert feature into a readable string."""
    properties = feature.get("properties", {})
    return f"""
Event: {properties.get('event', 'Unknown')}
Area: {properties.get('areaDesc', 'Unknown')}
Severity: {properties.get('severity', 'Unknown')}
Description: {properties.get('description', 'No description available')}
Instructions: {properties.get('instruction', 'No instructions available')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific state."""
    url = f"{NWS_API_URL}alerts/active?area={state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "No active alerts found."

    if not data["features"]:
        return "No active alerts found for the specified state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get the weather forecast for a specific latitude and longitude."""
    points_url = f"{NWS_API_URL}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:
        forecast = f"""
{period['name']}: 
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport='stdio')