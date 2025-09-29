"""
ITSM Adapter - Remedy Incident Gateway Integration
Provides REST API endpoints compatible with Remedy Incident Management
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ITSM Adapter - Remedy Integration",
    description="Adapter for Remedy Incident Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class IncidentCreateRequest(BaseModel):
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Incident description")
    priority: str = Field(..., description="Priority level (1-5)")
    category: str = Field(..., description="Incident category")
    requester: str = Field(..., description="Requester name")
    assigned_group: Optional[str] = Field(None, description="Assigned support group")
    impact: Optional[str] = Field(None, description="Impact level")
    urgency: Optional[str] = Field(None, description="Urgency level")

class IncidentUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, description="New status")
    priority: Optional[str] = Field(None, description="New priority")
    assigned_group: Optional[str] = Field(None, description="New assigned group")
    resolution: Optional[str] = Field(None, description="Resolution notes")
    work_notes: Optional[str] = Field(None, description="Work notes")

class IncidentResponse(BaseModel):
    incident_id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    requester: str
    assigned_group: Optional[str]
    impact: Optional[str]
    urgency: Optional[str]
    created_date: str
    updated_date: str
    resolution: Optional[str]

# Mock data for demonstration
mock_incidents = [
    {
        "incident_id": "INC0001",
        "title": "Database Connection Timeout",
        "description": "Users reporting slow response times from database queries",
        "status": "Assigned",
        "priority": "High",
        "category": "Database",
        "requester": "john.doe@company.com",
        "assigned_group": "Database Team",
        "impact": "Multiple Users",
        "urgency": "High",
        "created_date": "2024-01-15T10:30:00Z",
        "updated_date": "2024-01-15T14:45:00Z",
        "resolution": None
    },
    {
        "incident_id": "INC0002",
        "title": "Email Server Down",
        "description": "Email service is not responding",
        "status": "Resolved",
        "priority": "Critical",
        "category": "Email",
        "requester": "jane.smith@company.com",
        "assigned_group": "Infrastructure Team",
        "impact": "Department",
        "urgency": "Critical",
        "created_date": "2024-01-14T08:15:00Z",
        "updated_date": "2024-01-14T12:30:00Z",
        "resolution": "Restarted email service and cleared queue"
    }
]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "itsm-adapter"}

@app.get("/api/v1/incidents")
async def get_incidents(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_group: Optional[str] = Query(None, description="Filter by assigned group"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination")
) -> Dict[str, Any]:
    """
    Get incidents with optional filtering
    Compatible with Remedy Incident Gateway API
    """
    try:
        # Add correlation header for tracing
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        logger.info(f"Getting incidents - Correlation ID: {correlation_id}")

        # Filter incidents based on query parameters
        filtered_incidents = mock_incidents.copy()

        if status:
            filtered_incidents = [inc for inc in filtered_incidents if inc["status"].lower() == status.lower()]

        if priority:
            filtered_incidents = [inc for inc in filtered_incidents if inc["priority"].lower() == priority.lower()]

        if assigned_group:
            filtered_incidents = [inc for inc in filtered_incidents if inc.get("assigned_group", "").lower() == assigned_group.lower()]

        # Apply pagination
        total_count = len(filtered_incidents)
        paginated_incidents = filtered_incidents[offset:offset + limit]

        return {
            "incidents": paginated_incidents,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident(incident_id: str, request: Request) -> IncidentResponse:
    """
    Get a specific incident by ID
    Compatible with Remedy Incident Gateway API
    """
    try:
        # Add correlation header for tracing
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        logger.info(f"Getting incident {incident_id} - Correlation ID: {correlation_id}")

        # Find incident by ID
        incident = next((inc for inc in mock_incidents if inc["incident_id"] == incident_id), None)

        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

        return IncidentResponse(**incident)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/incidents")
async def create_incident(request_data: IncidentCreateRequest, request: Request) -> IncidentResponse:
    """
    Create a new incident
    Compatible with Remedy Incident Gateway API
    """
    try:
        # Add correlation header for tracing
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        logger.info(f"Creating incident - Correlation ID: {correlation_id}")

        # Generate new incident ID
        incident_id = f"INC{len(mock_incidents) + 1:04d}"

        # Create new incident
        new_incident = {
            "incident_id": incident_id,
            "title": request_data.title,
            "description": request_data.description,
            "status": "New",
            "priority": request_data.priority,
            "category": request_data.category,
            "requester": request_data.requester,
            "assigned_group": request_data.assigned_group,
            "impact": request_data.impact,
            "urgency": request_data.urgency,
            "created_date": datetime.utcnow().isoformat() + "Z",
            "updated_date": datetime.utcnow().isoformat() + "Z",
            "resolution": None
        }

        # Add to mock data
        mock_incidents.append(new_incident)

        logger.info(f"Created incident {incident_id}")
        return IncidentResponse(**new_incident)

    except Exception as e:
        logger.error(f"Error creating incident: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/v1/incidents/{incident_id}")
async def update_incident(
    incident_id: str,
    request_data: IncidentUpdateRequest,
    request: Request
) -> IncidentResponse:
    """
    Update an existing incident
    Compatible with Remedy Incident Gateway API
    """
    try:
        # Add correlation header for tracing
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        logger.info(f"Updating incident {incident_id} - Correlation ID: {correlation_id}")

        # Find incident by ID
        incident = next((inc for inc in mock_incidents if inc["incident_id"] == incident_id), None)

        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

        # Update fields
        update_data = request_data.dict(exclude_unset=True)
        incident.update(update_data)
        incident["updated_date"] = datetime.utcnow().isoformat() + "Z"

        # Handle status changes
        if request_data.status == "Resolved" and not incident.get("resolution"):
            incident["resolution"] = "Resolved via API"

        logger.info(f"Updated incident {incident_id}")
        return IncidentResponse(**incident)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/incidents/{incident_id}/close")
async def close_incident(incident_id: str, request: Request) -> IncidentResponse:
    """
    Close an incident
    Compatible with Remedy Incident Gateway API
    """
    try:
        # Add correlation header for tracing
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        logger.info(f"Closing incident {incident_id} - Correlation ID: {correlation_id}")

        # Find incident by ID
        incident = next((inc for inc in mock_incidents if inc["incident_id"] == incident_id), None)

        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

        # Update status to closed
        incident["status"] = "Closed"
        incident["updated_date"] = datetime.utcnow().isoformat() + "Z"
        incident["resolution"] = incident.get("resolution", "Closed via API")

        logger.info(f"Closed incident {incident_id}")
        return IncidentResponse(**incident)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/incidents/search")
async def search_incidents(
    request: Request,
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum number of results")
) -> Dict[str, Any]:
    """
    Search incidents by text query
    Compatible with Remedy Incident Gateway API
    """
    try:
        # Add correlation header for tracing
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        logger.info(f"Searching incidents with query '{query}' - Correlation ID: {correlation_id}")

        # Simple text search in title and description
        query_lower = query.lower()
        matching_incidents = [
            inc for inc in mock_incidents
            if query_lower in inc["title"].lower() or query_lower in inc["description"].lower()
        ]

        return {
            "incidents": matching_incidents[:limit],
            "total_count": len(matching_incidents),
            "query": query
        }

    except Exception as e:
        logger.error(f"Error searching incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import os
    # Use reload only in development
    reload = os.getenv("ENVIRONMENT", "production") == "development"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9020,
        reload=reload,
        log_level="info"
    )