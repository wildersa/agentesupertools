import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Observability Adapter",
    version="0.1.0",
    description="Mock adapter for observability data"
)

# Mock data - baseado nos endpoints reais do SolarWinds API Gateway
MOCK_ASSETS = [
    {
        "id": "server-01",
        "name": "Web Server 01",
        "type": "server",
        "location": "DC-A",
        "environment": "production",
        "tags": ["web", "nginx", "linux"],
        "ip_address": "192.168.1.10",
        "status": "Up",
        "vendor": "Dell",
        "model": "PowerEdge R740"
    },
    {
        "id": "server-02",
        "name": "Database Server 02",
        "type": "server",
        "location": "DC-B",
        "environment": "production",
        "tags": ["database", "postgresql", "linux"],
        "ip_address": "192.168.1.11",
        "status": "Up",
        "vendor": "HP",
        "model": "ProLiant DL380"
    },
    {
        "id": "server-03",
        "name": "Application Server 03",
        "type": "server",
        "location": "DC-A",
        "environment": "staging",
        "tags": ["app", "java", "tomcat"],
        "ip_address": "192.168.2.10",
        "status": "Warning",
        "vendor": "Dell",
        "model": "PowerEdge R640"
    },
    {
        "id": "app-01",
        "name": "Main Application",
        "type": "application",
        "location": "cloud",
        "environment": "production",
        "tags": ["microservice", "kubernetes", "aws"],
        "ip_address": "10.0.1.100",
        "status": "Up",
        "vendor": "AWS",
        "model": "EKS Cluster"
    },
    {
        "id": "db-01",
        "name": "Analytics Database",
        "type": "database",
        "location": "cloud",
        "environment": "production",
        "tags": ["analytics", "bigquery", "gcp"],
        "ip_address": "10.0.2.200",
        "status": "Up",
        "vendor": "Google Cloud",
        "model": "BigQuery"
    }
]

MOCK_METRICS = {
    "server-01": {
        "cpu": {"usage": 45.2, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "memory": {"usage": 67.8, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "warning"},
        "disk": {"usage": 23.1, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "network": {"usage": 12.5, "unit": "Mbps", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"}
    },
    "server-02": {
        "cpu": {"usage": 78.9, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "critical"},
        "memory": {"usage": 89.3, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "critical"},
        "disk": {"usage": 45.6, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "warning"},
        "network": {"usage": 25.8, "unit": "Mbps", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"}
    },
    "server-03": {
        "cpu": {"usage": 23.4, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "memory": {"usage": 34.7, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "disk": {"usage": 67.2, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "warning"},
        "network": {"usage": 8.9, "unit": "Mbps", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"}
    },
    "app-01": {
        "cpu": {"usage": 56.7, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "memory": {"usage": 72.1, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "warning"},
        "response_time": {"usage": 245.0, "unit": "ms", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "error_rate": {"usage": 0.02, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"}
    },
    "db-01": {
        "cpu": {"usage": 34.5, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "memory": {"usage": 45.8, "unit": "%", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "connections": {"usage": 127, "unit": "count", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"},
        "query_time": {"usage": 15.2, "unit": "ms", "timestamp": "2025-09-29T12:00:00Z", "status": "normal"}
    }
}

# Request/Response models
class AssetSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for assets")
    limit: int = Field(10, description="Maximum number of results", ge=1, le=100)

class AssetResponse(BaseModel):
    id: str
    name: str
    type: str
    location: str
    environment: str
    tags: List[str]

class AssetSearchResponse(BaseModel):
    assets: List[AssetResponse]
    total: int
    query: str

class MetricData(BaseModel):
    usage: float
    unit: str
    timestamp: str
    status: str

class MetricsResponse(BaseModel):
    asset_id: str
    metric_type: str
    data: MetricData

# Middleware para correlation ID
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    logger.info(f"Request started: {request.method} {request.url} correlation_id={correlation_id}")

    response = await call_next(request)

    response.headers["X-Correlation-ID"] = correlation_id
    logger.info(f"Request completed: status={response.status_code} correlation_id={correlation_id}")

    return response

# Middleware para simular latência realista
@app.middleware("http")
async def simulate_latency(request: Request, call_next):
    # Simular latência de 100-300ms
    latency = 0.1 + (0.2 * (hash(request.url.path) % 100) / 100)
    await asyncio.sleep(latency)
    return await call_next(request)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "observability-adapter"}

@app.post("/api/v1/nodes/query")
async def query_nodes(request: AssetSearchRequest) -> AssetSearchResponse:
    """Query nodes in the observability system (similar to SolarWinds API Gateway)."""
    logger.info(f"Querying nodes: query='{request.query}' limit={request.limit}")

    # Filtrar assets baseado na query
    filtered_assets = []
    for asset in MOCK_ASSETS:
        if (request.query.lower() in asset["name"].lower() or
            request.query.lower() in asset["type"].lower() or
            request.query.lower() in asset["location"].lower() or
            any(request.query.lower() in tag.lower() for tag in asset["tags"])):
            filtered_assets.append(asset)

    # Limitar resultados
    results = filtered_assets[:request.limit]

    response = AssetSearchResponse(
        assets=[AssetResponse(**asset) for asset in results],
        total=len(results),
        query=request.query
    )

    logger.info(f"Nodes query completed: results_count={len(results)} total_found={len(filtered_assets)}")

    return response

@app.get("/api/v1/nodes/{asset_id}/metrics")
async def get_node_metrics(asset_id: str, metric_type: str = "cpu") -> MetricsResponse:
    """Get metrics for a specific node (similar to SolarWinds API Gateway)."""
    logger.info(f"Getting node metrics: asset_id={asset_id} metric_type={metric_type}")

    # Validar se asset existe
    if asset_id not in MOCK_METRICS:
        logger.warning(f"Node not found: asset_id={asset_id}")
        raise HTTPException(status_code=404, detail=f"Node {asset_id} not found")

    # Validar se métrica existe para o asset
    asset_metrics = MOCK_METRICS[asset_id]
    if metric_type not in asset_metrics:
        logger.warning(f"Metric type not found for node: asset_id={asset_id} metric_type={metric_type}")
        raise HTTPException(status_code=404, detail=f"Metric type {metric_type} not found for node {asset_id}")

    metric_data = asset_metrics[metric_type]

    response = MetricsResponse(
        asset_id=asset_id,
        metric_type=metric_type,
        data=MetricData(**metric_data)
    )

    logger.info(f"Node metrics retrieved successfully: asset_id={asset_id} metric_type={metric_type} value={metric_data['usage']}")

    return response

@app.get("/api/v1/nodes/{asset_id}")
async def get_node(asset_id: str) -> AssetResponse:
    """Get details for a specific node (similar to SolarWinds API Gateway)."""
    logger.info(f"Getting node details: asset_id={asset_id}")

    for asset in MOCK_ASSETS:
        if asset["id"] == asset_id:
            return AssetResponse(**asset)

    logger.warning(f"Node not found: asset_id={asset_id}")
    raise HTTPException(status_code=404, detail=f"Node {asset_id} not found")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Observability Adapter on port 9010")
    uvicorn.run(app, host="0.0.0.0", port=9010, log_level="info")