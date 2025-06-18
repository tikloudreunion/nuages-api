from typing import List

from sqlmodel import Session, select

from .models import Nuage
from .schemas import CreateNuage, UpdateNuage

class NuageRepository:
    """Repository class for Nuage database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_uuid(self, nuage_uuid: str) -> Nuage | None:
        """Get a nuage by its UUID."""
        return self.session.exec(select(Nuage).where(Nuage.uuid == nuage_uuid)).first()

    def get_by_name(self, name: str) -> Nuage | None:
        """Get a nuage by its name."""
        return self.session.exec(select(Nuage).where(Nuage.name == name)).first()

    def get_all(self) -> List[Nuage]:
        """Get all .nuages."""
        return list(self.session.exec(select(Nuage)))

    def create(self, nuage_data: CreateNuage) -> Nuage:
        """Create a new nuage."""
        nuage = Nuage(**nuage_data.model_dump())
        self.session.add(nuage)
        self.session.commit()
        self.session.refresh(nuage)
        return nuage

    def update(self, nuage: Nuage, update_data: UpdateNuage) -> Nuage:
        """Update an existing nuage."""
        for field, value in update_data.model_dump().items():
            setattr(nuage, field, value)

        self.session.add(nuage)
        self.session.commit()
        self.session.refresh(nuage)
        return nuage

    def delete(self, nuage: Nuage) -> None:
        """Delete a nuage."""
        self.session.delete(nuage)
        self.session.commit()
