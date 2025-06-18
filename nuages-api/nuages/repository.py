from typing import List

from sqlmodel import Session, select

from .models import Nuage
from .schemas import CreateNuage


class NuageRepository:
    """Repository class for Nuage database operations."""

    def __init__(self, database_session: Session):
        self.database_session = database_session

    def get_by_uuid(self, nuage_uuid: str) -> Nuage | None:
        """Get a nuage by its UUID."""
        return self.database_session.exec(
            select(Nuage).where(Nuage.uuid == nuage_uuid)
        ).first()

    def get_by_name(self, name: str) -> Nuage | None:
        """Get a nuage by its name."""
        return self.database_session.exec(
            select(Nuage).where(Nuage.name == name)
        ).first()

    def get_all(self) -> List[Nuage]:
        """Get all .nuages."""
        return list(self.database_session.exec(select(Nuage)))

    def create(self, nuage_data: CreateNuage) -> Nuage:
        """Create a new nuage."""
        nuage = Nuage(
            name=nuage_data.name,
            node_name=nuage_data.node_name,
            template=nuage_data.template,
            cores=nuage_data.cores,
            memory=nuage_data.memory,
            swap=nuage_data.swap,
            disk=nuage_data.disk,
            vmid=nuage_data.vmid,
        )
        self.database_session.add(nuage)
        self.database_session.commit()
        self.database_session.refresh(nuage)
        return nuage

    def delete(self, nuage: Nuage) -> None:
        """Delete a nuage."""
        self.database_session.delete(nuage)
        self.database_session.commit()

    def get_last_vmid_by_node_name(
        self, node_name: str, default_vmid: int = 100
    ) -> int:
        """Get the last VMID for a specific node name."""
        last_vmid = self.database_session.exec(
            select(Nuage.vmid)
            .where(Nuage.node_name == node_name)
            .order_by(Nuage.vmid.desc())
        ).first()
        return last_vmid if last_vmid else default_vmid
