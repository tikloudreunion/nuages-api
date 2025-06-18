from pydantic import BaseModel, Field


class NuageBase(BaseModel):
    """Base schema for Nuage with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    template: str = Field(..., min_length=1, max_length=255)
    core: int = Field(default=1, ge=1, le=64)
    memory: int = Field(default=512, ge=256, le=32768)
    swap: int = Field(default=512, ge=0, le=16384)
    disk: int = Field(default=10240, ge=1024, le=1048576)


class CreateNuage(NuageBase):
    """Schema for creating a new nuage."""

    pass


class UpdateNuage(BaseModel):
    """Schema for updating an existing nuage."""

    core: int = Field(default=1, ge=1, le=64)
    memory: int = Field(default=512, ge=256, le=32768)
    swap: int = Field(default=512, ge=0, le=16384)
    disk: int = Field(default=10240, ge=1024, le=1048576)


class NuageResponse(NuageBase):
    """Schema for nuage responses."""

    uuid: str
