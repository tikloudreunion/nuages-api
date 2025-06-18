from typing import List

from fastapi import HTTPException, status

from .models import Nuage
from .schemas import CreateNuage, UpdateNuage
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
        """List all .nuages."""
        return self.repository.get_all()

    def update_nuage(self, nuage_uuid: str, update_data: UpdateNuage) -> Nuage:
        """Update a nuage."""
        nuage = self.get_nuage(nuage_uuid)  # This will raise 404 if not found
        return self.repository.update(nuage, update_data)

    def delete_nuage(self, nuage_uuid: str) -> None:
        """Delete a nuage."""
        nuage = self.get_nuage(nuage_uuid)  # This will raise 404 if not found
        self.repository.delete(nuage)
