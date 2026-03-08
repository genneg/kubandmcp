import asyncio
import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()

# Workaround per Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Importiamo l'agente che espone il tool "get_forecast"
from agent import agent

app = FastAPI()

# Serviamo la cartella static per l'interfaccia UI
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default_session")
    
    if not user_message:
        return {"response": "Messaggio vuoto"}
        
    try:
        runner = InMemoryRunner()
        response = await runner.run(
            agent=agent,
            user_input=user_message,
            session_id=session_id
        )
        return {"response": response.message.content.parts[0].text}
    except Exception as e:
        return {"response": f"Errore interno: {str(e)}"}
