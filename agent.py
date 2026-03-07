import httpx
from google.adk import Agent


async def get_forecast(
    latitude: float,
    longitude: float,
    daily: str = "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
    timezone: str = "Europe/Rome",
    forecast_days: int = 3,
) -> dict:
    """Ottieni le previsioni meteo da Open-Meteo per coordinate specifiche.

    Args:
        latitude: Latitudine della localita' (es. 41.89 per Roma).
        longitude: Longitudine della localita' (es. 12.48 per Roma).
        daily: Variabili giornaliere separate da virgola. Default include temperatura max/min, precipitazioni e codice meteo.
        timezone: Fuso orario per i risultati. Default: Europe/Rome.
        forecast_days: Numero di giorni di previsione (1-16). Default: 3.

    Returns:
        Dati meteo JSON con previsioni giornaliere.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": daily,
        "timezone": timezone,
        "forecast_days": forecast_days,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        resp.raise_for_status()
        return resp.json()


agent = Agent(
    name="assistente_meteo",
    model="gemini-3-flash-preview",
    tools=[get_forecast],
    instruction=(
        "Sei un assistente meteorologico esperto. "
        "Quando l'utente chiede il meteo di una citta', usa il tool get_forecast "
        "passando latitudine e longitudine della citta'. "
        "Rispondi sempre in italiano, in modo sintetico e leggibile. "
        "Formatta i dati in modo chiaro (temperatura, precipitazioni, condizioni)."
    ),
)
