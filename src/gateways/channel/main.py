import logging
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import structlog

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agents
try:
    from src.agents.main import AgentRouter
    agent_router = AgentRouter()
    logger.info("AgentRouter imported successfully")
except ImportError as e:
    logger.warning(f"Could not import AgentRouter: {e}, using mock responses")
    agent_router = None

app = FastAPI(
    title="Channel Gateway",
    version="0.1.0",
    description="Gateway for receiving messages from various channels (chat, web, app)"
)

# Security
security = HTTPBearer()

# Request/Response models
class MessageRequest(BaseModel):
    message: str = Field(..., description="The message content")
    channel: str = Field("chat", description="Channel type (chat, web, app)")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class MessageResponse(BaseModel):
    message_id: str
    response: str
    status: str = "success"
    timestamp: str

# Middleware para correlation ID
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    logger.info(f"Request started: {request.method} {request.url} correlation_id={correlation_id}")

    response = await call_next(request)

    response.headers["X-Correlation-ID"] = correlation_id
    logger.info(f"Request completed: status={response.status_code} correlation_id={correlation_id}")

    return response

# Dependency para autenticação simples
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token verification - in production this would validate JWT tokens."""
    token = credentials.credentials
    # For now, accept any token that starts with "Bearer "
    if not token or not token.startswith("test-token-"):
        logger.warning(f"Invalid token provided: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "channel-gateway"}

@app.post("/api/v1/messages", response_model=MessageResponse)
async def receive_message(
    request: MessageRequest,
    token: str = Depends(verify_token)
) -> MessageResponse:
    """Receive a message from a channel and route it to the appropriate agent."""
    message_id = str(uuid4())

    logger.info(f"Received message: id={message_id} channel={request.channel} user={request.user_id}")

    # Basic intent classification
    intent = classify_intent(request.message)

    logger.info(f"Classified intent: {intent} for message: {request.message[:50]}...")

    # Route to agent (for now, just mock response)
    response_text = await route_to_agent(intent, request.message, request.channel)

    return MessageResponse(
        message_id=message_id,
        response=response_text,
        timestamp="2025-09-29T12:00:00Z"
    )

def classify_intent(message: str) -> str:
    """Basic intent classification based on keywords."""
    message_lower = message.lower()

    # Observability intents
    if any(word in message_lower for word in ["cpu", "memória", "memory", "disco", "disk", "servidor", "server", "métrica", "metric"]):
        return "observability"

    # ITSM intents
    if any(word in message_lower for word in ["incidente", "incident", "ticket", "problema", "issue", "abrir", "create"]):
        return "itsm"

    # General intents
    if any(word in message_lower for word in ["ajuda", "help", "status", "ping"]):
        return "general"

    return "unknown"

async def route_to_agent(intent: str, message: str, channel: str) -> str:
    """Route the message to the appropriate agent and get response."""
    try:
        if agent_router:
            # Use real agent router
            response = await agent_router.route(message)
            return response.message
        else:
            # Fallback to mock responses
            return await route_to_mock_agent(intent, message, channel)

    except Exception as e:
        logger.error(f"Error routing to agent: {e}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde."

async def route_to_mock_agent(intent: str, message: str, channel: str) -> str:
    """Mock routing for fallback when agents are not available."""
    if intent == "observability":
        return await call_observability_agent(message)
    elif intent == "itsm":
        return await call_itsm_agent(message)
    elif intent == "general":
        return "Olá! Sou o Agente Super Tools. Posso ajudar com monitoramento de sistemas e gestão de incidentes. Como posso te ajudar?"
    else:
        return "Desculpe, não entendi sua solicitação. Tente perguntar sobre métricas de servidores ou criação de incidentes."

async def call_observability_agent(message: str) -> str:
    """Mock call to observability agent."""
    # This would eventually call the MCP broker
    if "cpu" in message.lower():
        return "Vou verificar as métricas de CPU. O servidor web-01 está com 45.2% de uso de CPU."
    elif "memória" in message.lower() or "memory" in message.lower():
        return "Verificando uso de memória. O servidor db-01 está com 67.8% de memória utilizada."
    else:
        return "Posso ajudar com métricas de CPU, memória, disco e rede dos servidores. Que informação você precisa?"

async def call_itsm_agent(message: str) -> str:
    """Mock call to ITSM agent."""
    # This would eventually call the MCP broker
    if "abrir" in message.lower() or "criar" in message.lower():
        return "Vou criar um incidente para você. Qual é o problema e em qual servidor?"
    elif "status" in message.lower():
        return "Verificando status do incidente. O INC-001 está em andamento."
    else:
        return "Posso ajudar com criação, atualização e consulta de incidentes. O que você gostaria de fazer?"

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Channel Gateway on port 9200")
    uvicorn.run(app, host="0.0.0.0", port=9200, log_level="info")