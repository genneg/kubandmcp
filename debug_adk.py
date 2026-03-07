import logging
import asyncio
import sys
from google.genai import types
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logging.basicConfig(level=logging.DEBUG)

async def run():
    from agent import create_agent_and_toolset
    agent, mcp_toolset = create_agent_and_toolset()
    
    runner = InMemoryRunner(agent=agent, app_name='testApp')
    session = await runner.session_service.create_session(
        app_name="testApp",
        user_id="u"
    )
    
    print("Testing ADK pipeline...")
    try:
        async for e in runner.run_async(
            user_id='u', 
            session_id=session.id, 
            new_message=types.Content(role="user", parts=[types.Part.from_text(text='Che tempo fa a Roma domani?')])
        ):
            print("EVENT:", e)
    except Exception as ex:
        print("EXCEPTION:", ex)
    finally:
        await mcp_toolset.close()

if __name__ == "__main__":
    asyncio.run(run())
