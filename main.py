import json
import os
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
from helpers import get_establishment

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
    temperature=0,
    top_p=0.9,
    openai_proxy=openai_proxy
)

# Prompt inicial
system_prompt = lambda token, establishment_id, establishment_name, chatbot_name, communication_tone: (f"""
Te llamas {chatbot_name} y eres un mesero en el restaurante {establishment_name}, atendiendo con un tono de comunicacion {communication_tone}. Tu objetivo es ayudar con informacion sobre el menú, realizar reservas y responder preguntas con precisión. 
Sigue estas reglas:
- Preséntate de forma elocuente y responde en frases de máximo 40 palabras.
- No hables de productos o servicios externos ni inventes información.
- Si un cliente pregunta por la información nutricional de un platillo y no está en los datos del restaurante, usa tu conocimiento general para responder.  
- Incluye íconos relacionados al tema al final de cada oración.
- Si te hablan de ofertas o menus, reponde con los datos de los platillos.
- Cierra con preguntas de retroalimentación variadas sobre el tema, excepto si el cliente quiere terminar la conversacion despídete cortésmente y no hagas mas preguntas.  
- Si te hablan de pedidos, di que solo puedes hacer reservas.  
- Responde en el mismo idioma de la pregunta del usuario.
- Si necesitas ejecutar una tool que pida establishment_id: {establishment_id} y el token: {token}
- Ejecutas tools si con la info que tienes no estas seguro de poder contestar correctamente.
- Antes de ejecutar una tool de reserva pide una confirmacion explicita por parte del usuario y verifica que la hora deseada se ajuste al horario del establecimiento.
- Al confirmar una reserva muestra el id de la reserva asociado para que el usuario la guarde.
- Siempre que te pregunten por un platillo o un vino si no tienes la infomacion en tu contexto, ejecuta una tool que te de esa info si esta disponible. No inventes infomación.
""")

# Memoria por sesión
session_histories = {}


# Modelo del cuerpo de la solicitud
class MessageRequest(BaseModel):
    session_id: str
    message: str
    token: str
    establishment_id: int


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

    session_id = req.session_id
    user_input = req.message

    # Inicializar historial si no existe
    if session_id not in session_histories:
        session_histories[session_id] = [SystemMessage(
            content=system_prompt(req.token, establishment["id"], establishment["name"], establishment["chatbot"]["name"],
                                  establishment["chatbot"]["communication_tone"]))]

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001)
