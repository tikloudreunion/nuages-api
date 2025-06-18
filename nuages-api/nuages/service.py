from typing import List

from fastapi import HTTPException, status

from .models import Nuage
from .schemas import CreateNuage, UpdateNuage, NuageStatus
from .repository import NuageRepository


class NuageService:
    """Service class for Nuage business logic."""

    def __init__(self, repository: NuageRepository):
        self.repository = repository

    def create_nuage(self, nuage_data: CreateNuage) -> Nuage:
        """Create a new nuage with validation."""
        existing_nuage = self.repository.get_by_name(nuage_data.name)
        if existing_nuage:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A nuage with name '{nuage_data.name}' already exists.",
            )

        return self.repository.create(nuage_data)

    def get_nuage(self, nuage_uuid: str) -> Nuage:
        """Get a nuage by UUID."""
        nuage = self.repository.get_by_uuid(nuage_uuid)
        if not nuage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nuage with UUID '{nuage_uuid}' not found.",
            )
        return nuage

    def list_nuages(self) -> List[Nuage]:
        """List all nuages."""
        return self.repository.get_all()

    def get_nuage_status(self, nuage_uuid: str) -> NuageStatus:
        """Get the status of a nuage."""
        # nuage = self.repository.get_by_uuid(nuage_uuid)
        # if not nuage:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Nuage with UUID '{nuage_uuid}' not found.",
        #     )
        # pass

        ### !  Placeholder logic for status retrieval
        status1 = NuageStatus(
            status="running",
            message="Nuage is running.",
            cpu_usage=50.0,
            memory_usage=30.0,
            disk_usage=20.0,
        )
        status2 = NuageStatus(
            status="stopped",
            message="Nuage is stopped.",
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
        )
        status3 = NuageStatus(
            status="error",
            message="Nuage encountered an error.",
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
        )
        return [status1, status2, status3][int(nuage_uuid)]

    def update_nuage(self, nuage_uuid: str, update_data: UpdateNuage) -> Nuage:
        """Update a nuage."""
        nuage = self.get_nuage(nuage_uuid)
        return self.repository.update(nuage, update_data)

    def delete_nuage(self, nuage_uuid: str) -> None:
        """Delete a nuage."""
        nuage = self.get_nuage(nuage_uuid)
        self.repository.delete(nuage)

    def start_nuage(self, nuage_uuid: str) -> Nuage:
        """Activate a nuage."""
        pass

    def stop_nuage(self, nuage_uuid: str) -> Nuage:
        """Deactivate a nuage."""
        pass

    def restart_nuage(self, nuage_uuid: str) -> Nuage:
        """Restart a nuage."""
        self.stop_nuage(nuage_uuid)
        return self.start_nuage(nuage_uuid)
