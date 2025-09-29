import logging
from typing import Any, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class Intent(Enum):
    OBSERVABILITY = "observability"
    ITSM = "itsm"
    GENERAL = "general"
    UNKNOWN = "unknown"

class AgentResponse:
    def __init__(self, message: str, success: bool = True, data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.success = success
        self.data = data or {}

class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str):
        self.name = name

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a message and return a response."""
        raise NotImplementedError

class IntentClassifierAgent(BaseAgent):
    """Agent responsible for classifying message intents."""

    def __init__(self):
        super().__init__("intent_classifier")

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Classify the intent of a message."""
        intent = self._classify_intent(message)

        logger.info(f"Classified intent: {intent.value} for message: {message[:50]}...")

        return AgentResponse(
            message=f"Intent classified as: {intent.value}",
            success=True,
            data={"intent": intent.value}
        )

    def _classify_intent(self, message: str) -> Intent:
        """Classify message intent based on keywords."""
        message_lower = message.lower()

        # Observability intents
        observability_keywords = [
            "cpu", "memória", "memory", "disco", "disk", "servidor", "server",
            "métrica", "metric", "monitor", "status", "performance", "load",
            "uptime", "ping", "latency", "throughput", "bandwidth"
        ]
        if any(keyword in message_lower for keyword in observability_keywords):
            return Intent.OBSERVABILITY

        # ITSM intents
        itsm_keywords = [
            "incidente", "incident", "ticket", "problema", "issue", "abrir", "create",
            "atualizar", "update", "resolver", "resolve", "fechar", "close",
            "status", "prioridade", "priority", "sla", "escalation"
        ]
        if any(keyword in message_lower for keyword in itsm_keywords):
            return Intent.ITSM

        # General intents
        general_keywords = ["ajuda", "help", "oi", "olá", "hello", "hi", "ping"]
        if any(keyword in message_lower for keyword in general_keywords):
            return Intent.GENERAL

        return Intent.UNKNOWN

class ObservabilityAgent(BaseAgent):
    """Agent for handling observability-related requests."""

    def __init__(self):
        super().__init__("observability")

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process observability requests by calling MCP broker."""
        try:
            # For now, mock the MCP broker call
            response = await self._call_mcp_broker(message)

            return AgentResponse(
                message=response,
                success=True,
                data={"source": "mcp_broker", "intent": "observability"}
            )

        except Exception as e:
            logger.error(f"Error in observability agent: {e}")
            return AgentResponse(
                message="Desculpe, ocorreu um erro ao consultar as métricas. Tente novamente.",
                success=False,
                data={"error": str(e)}
            )

    async def _call_mcp_broker(self, message: str) -> str:
        """Mock call to MCP broker - in production this would make HTTP calls."""
        message_lower = message.lower()

        # Simulate different responses based on message content
        if "cpu" in message_lower:
            return "📊 Métricas de CPU:\n• Servidor web-01: 45.2% (Normal)\n• Servidor db-02: 78.9% (Crítico)\n• Servidor app-03: 23.4% (Normal)"

        elif "memória" in message_lower or "memory" in message_lower:
            return "🧠 Uso de Memória:\n• Servidor web-01: 67.8% (Aviso)\n• Servidor db-02: 89.3% (Crítico)\n• Servidor app-03: 34.7% (Normal)"

        elif "disco" in message_lower or "disk" in message_lower:
            return "💾 Espaço em Disco:\n• Servidor web-01: 23.1% usado\n• Servidor db-02: 45.6% usado\n• Servidor app-03: 67.2% usado"

        elif "servidor" in message_lower or "server" in message_lower:
            return "🖥️ Status dos Servidores:\n• web-01: Online\n• db-02: Online (com alertas)\n• app-03: Online\n• Todos os sistemas monitorados estão operacionais."

        else:
            return "Posso ajudar com métricas de CPU, memória, disco e status dos servidores. Que informação específica você precisa?"

class ITSMAgent(BaseAgent):
    """Agent for handling ITSM-related requests."""

    def __init__(self):
        super().__init__("itsm")

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process ITSM requests by calling MCP broker."""
        try:
            # For now, mock the MCP broker call
            response = await self._call_mcp_broker(message)

            return AgentResponse(
                message=response,
                success=True,
                data={"source": "mcp_broker", "intent": "itsm"}
            )

        except Exception as e:
            logger.error(f"Error in ITSM agent: {e}")
            return AgentResponse(
                message="Desculpe, ocorreu um erro ao processar sua solicitação de incidente. Tente novamente.",
                success=False,
                data={"error": str(e)}
            )

    async def _call_mcp_broker(self, message: str) -> str:
        """Mock call to MCP broker - in production this would make HTTP calls."""
        message_lower = message.lower()

        # Simulate different ITSM responses
        if "abrir" in message_lower or "criar" in message_lower or "create" in message_lower:
            return "🎫 Criando incidente...\n✅ Incidente INC-001234 criado com sucesso!\n📝 Título: Problema reportado pelo usuário\n🔴 Prioridade: Alta\n👤 Responsável: Equipe de Infraestrutura\n📞 Você será notificado sobre atualizações."

        elif "status" in message_lower:
            return "📋 Status do Incidente:\n🎫 INC-001234: Em andamento\n🔴 Prioridade: Alta\n👤 Responsável: João Silva\n📅 Criado em: 2025-09-29 10:30\n📝 Última atualização: Investigando possível problema de conectividade"

        elif "atualizar" in message_lower or "update" in message_lower:
            return "📝 Atualizando incidente INC-001234...\n✅ Status alterado para: Em resolução\n📋 Adicionada nota: Problema identificado no servidor db-02\n👤 Responsável: Equipe de Banco de Dados"

        elif "resolver" in message_lower or "resolve" in message_lower:
            return "✅ Resolvendo incidente INC-001234...\n🎉 Incidente resolvido com sucesso!\n📝 Solução: Reiniciado serviço de banco de dados\n⭐ Satisfação do cliente: 5/5"

        else:
            return "Posso ajudar com:\n• Criar novos incidentes\n• Consultar status de incidentes\n• Atualizar incidentes existentes\n• Resolver incidentes\n\nQue operação você gostaria de realizar?"

class GeneralAgent(BaseAgent):
    """Agent for handling general requests."""

    def __init__(self):
        super().__init__("general")

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process general requests."""
        return AgentResponse(
            message="""Olá! 👋 Sou o Agente Super Tools, seu assistente para Suporte e Cliente.

Posso ajudar com:

🔍 **Monitoramento e Observabilidade:**
• Verificar métricas de CPU, memória e disco
• Status dos servidores
• Performance do sistema

🎫 **Gestão de Incidentes:**
• Criar novos incidentes
• Consultar status de tickets
• Atualizar incidentes
• Resolver problemas

💬 **Como usar:**
• "Qual o status da CPU do servidor web-01?"
• "Abrir incidente para problema no banco de dados"
• "Status do incidente INC-001234"

O que você gostaria de fazer hoje?""",
            success=True,
            data={"intent": "general"}
        )

class AgentRouter:
    """Router for directing messages to appropriate agents."""

    def __init__(self):
        self.intent_classifier = IntentClassifierAgent()
        self.observability_agent = ObservabilityAgent()
        self.itsm_agent = ITSMAgent()
        self.general_agent = GeneralAgent()

    async def route(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Route message to appropriate agent based on intent."""
        # First, classify the intent
        intent_response = await self.intent_classifier.process(message, context)
        intent = intent_response.data.get("intent", "unknown")

        logger.info(f"Routing message to agent for intent: {intent}")

        # Route to specific agent
        if intent == "observability":
            return await self.observability_agent.process(message, context)
        elif intent == "itsm":
            return await self.itsm_agent.process(message, context)
        elif intent == "general":
            return await self.general_agent.process(message, context)
        else:
            # Fallback to general agent for unknown intents
            return await self.general_agent.process(message, context)