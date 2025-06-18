from pydantic import BaseModel, Field


class NuageBase(BaseModel):
    """Base schema for Nuage with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    template: str = Field(..., min_length=1, max_length=255)
    cores: int = Field(default=1, ge=1, le=64)
    memory: int = Field(default=512, ge=256, le=32768)
    swap: int = Field(default=512, ge=0, le=16384)
    disk: int = Field(default=10240, ge=1024, le=1048576)


class CreateNuageRequest(NuageBase):
    """Schema for creating a new nuage."""

    pass


class CreateNuage(NuageBase):
    """Schema for creating a new nuage."""

    node_name: str
    vmid: int


class NuageResponse(NuageBase):
    """Schema for nuage responses."""

    uuid: str

class NuageStatus(BaseModel):
    """Model for the Nuage current status."""
    status: str = Field(
        ...,
        description="Current status of the nuage, can be 'running', 'stopped', or 'error'",
        pattern=r"^(running|stopped|error)$",
    )
    message: str = Field(
        description="Additional message about the current status",
    )
    cpu_usage: float = Field(
        ge=0.0,
        le=100.0,
        description="Current CPU usage percentage of the nuage",
    )
    memory_usage: float = Field(
        ge=0.0,
        le=100.0,
        description="Current memory usage percentage of the nuage",
    )
    disk_usage: float = Field(
        ge=0.0,
        le=100.0,
        description="Current disk usage percentage of the nuage",
    )