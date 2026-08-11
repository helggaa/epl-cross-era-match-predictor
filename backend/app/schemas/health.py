from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    project: str
    version: str
    database_connected: bool
