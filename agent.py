from google.adk import Agent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

def create_agent_and_toolset():
    mcp_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "node:18-alpine",
                "npx",
                "-y",
                "@openapi-mcp/server",
                "https://raw.githubusercontent.com/open-meteo/open-meteo/main/openapi.yml"
            ]
        )
    )

    # Rimosso tool_filter momentaneamente per vedere l'esatta stringa generata dal server
    mcp_toolset = McpToolset(
        connection_params=mcp_params
    )

    agent = Agent(
        name="assistente_meteo",
        model="gemini-3-flash-preview",
        tools=[mcp_toolset],
        instruction="Sei un assistente meteorologico. Usa gli strumenti per ottenere i dati meteo. Rispondi in italiano in modo sintetico e preciso."
    )
    
    return agent, mcp_toolset
