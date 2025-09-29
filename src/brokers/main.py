import asyncio
import logging
from typing import Any, Dict

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configurar logging estruturado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastMCP broker
app = FastMCP(
    name="Agent Super Tools MCP Broker",
    version="0.1.0"
)


# Modelos para tools
class SearchAssetsRequest(BaseModel):
    query: str = Field(..., description="Search query for assets")
    limit: int = Field(10, description="Maximum number of results")


class GetMetricsRequest(BaseModel):
    asset_id: str = Field(..., description="Asset ID to get metrics for")
    metric_type: str = Field("cpu", description="Type of metric (cpu, memory, disk)")


class SearchIncidentsRequest(BaseModel):
    query: str = Field(..., description="Search query for incidents")
    status: str = Field(None, description="Filter by status")
    priority: str = Field(None, description="Filter by priority")
    limit: int = Field(10, description="Maximum number of results")


class CreateIncidentRequest(BaseModel):
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Incident description")
    priority: str = Field(..., description="Priority level")
    category: str = Field(..., description="Incident category")
    requester: str = Field(..., description="Requester name")


class UpdateIncidentRequest(BaseModel):
    incident_id: str = Field(..., description="Incident ID to update")
    status: str = Field(None, description="New status")
    priority: str = Field(None, description="New priority")
    resolution: str = Field(None, description="Resolution notes")


# Tools que chamam o adapter de observability
@app.tool()
async def observ_search_assets(request: SearchAssetsRequest) -> Dict[str, Any]:
    """Search for assets in the observability system."""
    logger.info("Tool called: observ_search_assets", extra={"query": request.query, "limit": request.limit})

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://observability-adapter:9010/api/v1/nodes/query",
                json={"query": request.query, "limit": request.limit},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return data
    except Exception as e:
        logger.error("Failed to call observability adapter", extra={"error": str(e)})
        # Fallback para dados mockados
        mock_assets = [
            {"id": "server-01", "name": "Web Server 01", "type": "server", "location": "DC-A"},
            {"id": "server-02", "name": "DB Server 02", "type": "server", "location": "DC-B"},
            {"id": "app-01", "name": "Main Application", "type": "application", "location": "cloud"},
        ]
        results = [asset for asset in mock_assets if request.query.lower() in asset["name"].lower()][:request.limit]
        return {
            "assets": results,
            "total": len(results),
            "query": request.query
        }


@app.tool()
async def observ_get_metrics(request: GetMetricsRequest) -> Dict[str, Any]:
    """Get metrics for a specific asset."""
    logger.info("Tool called: observ_get_metrics", extra={"asset_id": request.asset_id, "metric_type": request.metric_type})

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://observability-adapter:9010/api/v1/nodes/{request.asset_id}/metrics",
                params={"metric_type": request.metric_type},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return data
    except Exception as e:
        logger.error("Failed to call observability adapter", extra={"error": str(e), "asset_id": request.asset_id})
        # Fallback para dados mockados
        mock_metrics = {
            "cpu": {"usage": 45.2, "unit": "%", "timestamp": "2025-09-29T12:00:00Z"},
            "memory": {"usage": 67.8, "unit": "%", "timestamp": "2025-09-29T12:00:00Z"},
            "disk": {"usage": 23.1, "unit": "%", "timestamp": "2025-09-29T12:00:00Z"},
        }
        metric = mock_metrics.get(request.metric_type, {"error": "Metric type not found"})
        return {
            "asset_id": request.asset_id,
            "metric_type": request.metric_type,
            "data": metric
        }


@app.tool()
async def itsm_search_incidents(request: SearchIncidentsRequest) -> Dict[str, Any]:
    """Search for incidents in the ITSM system."""
    logger.info("Tool called: itsm_search_incidents", extra={
        "query": request.query,
        "status": request.status,
        "priority": request.priority,
        "limit": request.limit
    })

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            params = {"query": request.query, "limit": request.limit}
            if request.status:
                params["status"] = request.status
            if request.priority:
                params["priority"] = request.priority

            response = await client.get(
                "http://itsm-adapter:9020/api/v1/incidents/search",
                params=params,
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return data
    except Exception as e:
        logger.error("Failed to call ITSM adapter", extra={"error": str(e)})
        # Fallback para dados mockados
        mock_incidents = [
            {
                "incident_id": "INC0001",
                "title": "Database Connection Timeout",
                "status": "Assigned",
                "priority": "High",
                "description": "Users reporting slow response times"
            },
            {
                "incident_id": "INC0002",
                "title": "Email Server Down",
                "status": "Resolved",
                "priority": "Critical",
                "description": "Email service is not responding"
            }
        ]
        results = [inc for inc in mock_incidents if request.query.lower() in inc["title"].lower()][:request.limit]
        return {
            "incidents": results,
            "total_count": len(results),
            "query": request.query
        }


@app.tool()
async def itsm_create_incident(request: CreateIncidentRequest) -> Dict[str, Any]:
    """Create a new incident in the ITSM system."""
    logger.info("Tool called: itsm_create_incident", extra={
        "title": request.title,
        "priority": request.priority,
        "category": request.category
    })

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://itsm-adapter:9020/api/v1/incidents",
                json={
                    "title": request.title,
                    "description": request.description,
                    "priority": request.priority,
                    "category": request.category,
                    "requester": request.requester
                },
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return data
    except Exception as e:
        logger.error("Failed to call ITSM adapter", extra={"error": str(e)})
        # Fallback para dados mockados
        return {
            "incident_id": "INC9999",
            "title": request.title,
            "description": request.description,
            "status": "New",
            "priority": request.priority,
            "category": request.category,
            "requester": request.requester,
            "created_date": "2024-01-15T10:30:00Z",
            "message": "Incident created (mock fallback)"
        }


@app.tool()
async def itsm_update_incident(request: UpdateIncidentRequest) -> Dict[str, Any]:
    """Update an existing incident in the ITSM system."""
    logger.info("Tool called: itsm_update_incident", extra={
        "incident_id": request.incident_id,
        "status": request.status,
        "priority": request.priority
    })

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            update_data = {}
            if request.status:
                update_data["status"] = request.status
            if request.priority:
                update_data["priority"] = request.priority
            if request.resolution:
                update_data["resolution"] = request.resolution

            response = await client.put(
                f"http://itsm-adapter:9020/api/v1/incidents/{request.incident_id}",
                json=update_data,
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return data
    except Exception as e:
        logger.error("Failed to call ITSM adapter", extra={"error": str(e), "incident_id": request.incident_id})
        # Fallback para dados mockados
        return {
            "incident_id": request.incident_id,
            "status": request.status or "Updated",
            "priority": request.priority,
            "resolution": request.resolution,
            "updated_date": "2024-01-15T14:45:00Z",
            "message": "Incident updated (mock fallback)"
        }


@app.tool()
async def health_check() -> Dict[str, Any]:
    """Check the health status of the MCP Broker."""
    logger.info("Tool called: health_check")
    return {"status": "healthy", "service": "mcp-broker", "timestamp": "2025-09-29T12:00:00Z"}


# Health check endpoint adicional (não MCP)
from fastapi import FastAPI
from fastapi.responses import JSONResponse

fastapi_app = FastAPI(title="MCP Broker Health", version="0.1.0")

@fastapi_app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy", "service": "mcp-broker"})


def main():
    """Entry point for running the MCP broker."""
    import uvicorn

    # Configurar logging estruturado
    import structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger.info("Starting MCP Broker", extra={"port": 9000})

    # Rodar servidor MCP (não usar mount por enquanto)
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")


if __name__ == "__main__":
    main()