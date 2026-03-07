import asyncio
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main() -> None:
    from agent import agent

    runner = InMemoryRunner(agent=agent, app_name="AssistenteMeteoCLI")

    session = await runner.session_service.create_session(
        app_name="AssistenteMeteoCLI",
        user_id="local_user",
    )
    session_id = session.id

    print("Assistente Meteo | ADK + Gemini + Open-Meteo")
    print(f"Session ID: {session_id}")
    print("Digita 'esci' per uscire.\n")

    try:
        while True:
            try:
                user_input = input("Tu: ")
            except EOFError:
                break

            if user_input.strip().lower() in ("esci", "quit", "exit"):
                break

            if not user_input.strip():
                continue

            print("Agente: ", end="", flush=True)

            try:
                async for event in runner.run_async(
                    user_id="local_user",
                    session_id=session_id,
                    new_message=types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=user_input)],
                    ),
                ):
                    if event.is_final_response() and event.content:
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                print(part.text, end="", flush=True)

            except Exception as e:
                print(f"\n[Errore: {e}]")

            print()

    except KeyboardInterrupt:
        print("\n\nInterruzione manuale.")


if __name__ == "__main__":
    asyncio.run(main())
