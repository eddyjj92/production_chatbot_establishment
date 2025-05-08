import json
import os
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from contextlib import asynccontextmanager
from redis import Redis
from starlette.staticfiles import StaticFiles
from helpers import get_establishment, get_establishments
from prompts import system_prompt_reservation, system_prompt_in_establishment

# Conexión a Redis
redis = Redis(host='82.29.197.144', port=6379, db=0, decode_responses=True)

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEVELOPMENT = os.getenv("DEVELOPMENT")
openai_proxy = None

if DEVELOPMENT == 'True':
    openai_proxy = "http://localhost:5000"

# Configurar el modelo
model = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0.2,
    top_p=0.75,
    openai_proxy=openai_proxy
)

# Memoria por sesión
session_histories = {}


# Modelo del cuerpo de la solicitud
class MessageRequest(BaseModel):
    session_id: str
    message: str
    token: str
    establishment_id: int
    prompt_variant: Literal['reservation', 'in_establishment']


class EstablishmentsRequest(BaseModel):
    token: str


# Context manager para manejar eventos de inicio y cierre de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

    # Inicializar herramientas y agente
    app.state.client = await MultiServerMCPClient({
        "mcp": {
            # make sure you start your weather server on port 8000
            "url": f"{MCP_SERVER_URL}/sse",
            "transport": "sse"
        }
    }).__aenter__()

    tools = app.state.client.get_tools()
    memory = MemorySaver()
    app.state.agent = create_react_agent(model, tools=tools, checkpointer=memory)

    yield

    await app.state.client.__aexit__(None, None, None)


# Crear la aplicación FastAPI
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(req: MessageRequest, request: Request):
    establishment = get_establishment(req.establishment_id, req.token)
    print(establishment)
    if establishment.get("error"):
        print(f"""Error: {establishment["error"]}""")
        return {"error": establishment["error"]}

    session_id = f"""{req.session_id}_{req.prompt_variant}_{establishment["id"]}"""
    user_input = req.message

    # Inicializar historial si no existe
    if session_id not in session_histories:
        system_prompt = {
            "reservation": system_prompt_reservation,
            "in_establishment": system_prompt_in_establishment
        }

        session_histories[session_id] = [SystemMessage(
            content=system_prompt[req.prompt_variant](
                req.token, establishment["id"], establishment["name"],
                establishment["chatbot"]["name"], establishment["chatbot"]["communication_tone"]
            )
        )]

    # Añadir el mensaje del usuario
    history = session_histories[session_id]
    history.append(HumanMessage(content=user_input))

    # Limitar historial a últimos 6 mensajes + prompt
    trimmed = [history[0]] + [msg for msg in history[1:] if isinstance(msg, (HumanMessage, AIMessage))][-6:]

    try:
        response = await request.app.state.agent.ainvoke(
            {"messages": trimmed},
            config={"configurable": {"thread_id": session_id}},
        )

        # Añadir respuesta del agente al historial
        ai_msg = response["messages"][-1]
        session_histories[session_id].append(ai_msg)

        reservation = None
        if response["messages"][-2].type == "tool" and response["messages"][-2].content:
            tool_name = response["messages"][-2].name

            if tool_name == 'create_reservation':
                reservation = response["messages"][-2].content

        return {
            "response": ai_msg,
            "reservation": reservation,
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/establishments")
async def chat(req: EstablishmentsRequest):
    establishments = get_establishments(req.token)
    print(establishments)
    if establishments.get("error"):
        print(f"""Error: {establishments["error"]}""")
        return {"error": establishments["error"]}

    return {
        "establishments": establishments,
    }


class CustomStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)

        # Forzar el tipo MIME correcto para archivos JS
        if path.endswith(".js"):
            response.headers["Content-Type"] = "application/javascript"
        return response


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/assets", CustomStaticFiles(directory=os.path.join(BASE_DIR, "public/spa/assets")), name="assets")
app.mount("/", CustomStaticFiles(directory=os.path.join(BASE_DIR, "public/spa"), html=True, check_dir=True), name="spa")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001)
