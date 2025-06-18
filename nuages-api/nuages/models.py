from uuid import uuid4
from time import time

from sqlmodel import SQLModel, Field


class Nuage(SQLModel, table=True):
    """Database model for Nuage resources."""

    uuid: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique identifier for the nuage",
    )
    name: str = Field(
        unique=True,
        index=True,
        description="Name of the nuage, must be unique",
    )
    node_name: str = Field(
        description="Name of the Proxmox node where the nuage is hosted",
    )
    vmid: int = Field(
        unique=True,
        index=True,
        description="Virtual Machine ID for the nuage, must be unique",
        ge=100,
        lt=999999999,
    )
    template: str = Field(description="Template used for the nuage")
    cores: int = Field(default=1, ge=1, description="Cores count of the nuage")
    memory: int = Field(default=512, ge=256, description="Memory size in MB")
    swap: int = Field(default=512, ge=0, description="Swap size in MB")
    disk: int = Field(default=10240, ge=1024, description="Disk size in MB")
    created_at: float = Field(
        default_factory=time,
        description="Timestamp when the nuage was created",
        index=True,
    )
    updated_at: float = Field(
        default_factory=time,
        description="Timestamp when the nuage was last updated",
    )
