import logging
from typing import List
from sqlmodel import Session, select
from .models import Nuage
from .schemas import CreateNuage

# Set up logger for this module
logger = logging.getLogger(__name__)


class NuageRepository:
    """Repository class for Nuage database operations."""

    def __init__(self, database_session: Session):
        self.database_session = database_session
        logger.info("NuageRepository initialized")

    def get_by_uuid(self, nuage_uuid: str) -> Nuage | None:
        """Get a nuage by its UUID."""
        logger.debug(f"Searching for nuage with UUID: {nuage_uuid}")

        try:
            nuage = self.database_session.exec(
                select(Nuage).where(Nuage.uuid == nuage_uuid)
            ).first()

            if nuage:
                logger.info(f"Found nuage with UUID {nuage_uuid}: {nuage.name}")
            else:
                logger.warning(f"No nuage found with UUID: {nuage_uuid}")

            return nuage

        except Exception as e:
            logger.error(f"Error retrieving nuage by UUID {nuage_uuid}: {str(e)}")
            raise

    def get_by_name(self, name: str) -> Nuage | None:
        """Get a nuage by its name."""
        logger.debug(f"Searching for nuage with name: {name}")

        try:
            nuage = self.database_session.exec(
                select(Nuage).where(Nuage.name == name)
            ).first()

            if nuage:
                logger.info(f"Found nuage with name '{name}': UUID {nuage.uuid}")
            else:
                logger.warning(f"No nuage found with name: {name}")

            return nuage

        except Exception as e:
            logger.error(f"Error retrieving nuage by name '{name}': {str(e)}")
            raise

    def get_all(self) -> List[Nuage]:
        """Get all nuages."""
        logger.debug("Retrieving all nuages")

        try:
            nuages = list(self.database_session.exec(select(Nuage)))
            logger.info(f"Retrieved {len(nuages)} nuages from database")
            return nuages

        except Exception as e:
            logger.error(f"Error retrieving all nuages: {str(e)}")
            raise

    def create(self, nuage_data: CreateNuage) -> Nuage:
        """Create a new nuage."""
        logger.info(f"Creating new nuage: {nuage_data.name}")
        logger.debug(f"Nuage creation data: {nuage_data}")

        try:
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
            logger.debug(f"Added nuage {nuage_data.name} to session")

            self.database_session.commit()
            logger.debug(f"Committed nuage {nuage_data.name} to database")

            self.database_session.refresh(nuage)
            logger.info(
                f"Successfully created nuage '{nuage.name}' with UUID: {nuage.uuid}"
            )

            return nuage

        except Exception as e:
            logger.error(f"Error creating nuage '{nuage_data.name}': {str(e)}")
            self.database_session.rollback()
            logger.debug("Database session rolled back due to error")
            raise

    def delete(self, nuage: Nuage) -> None:
        """Delete a nuage."""
        logger.info(f"Deleting nuage: {nuage.name} (UUID: {nuage.uuid})")

        try:
            self.database_session.delete(nuage)
            logger.debug(f"Marked nuage {nuage.name} for deletion")

            self.database_session.commit()
            logger.info(f"Successfully deleted nuage: {nuage.name}")

        except Exception as e:
            logger.error(f"Error deleting nuage '{nuage.name}': {str(e)}")
            self.database_session.rollback()
            logger.debug("Database session rolled back due to error")
            raise

    def get_last_vmid_by_node_name(
        self, node_name: str, default_vmid: int = 100
    ) -> int:
        """Get the last VMID for a specific node name."""
        logger.debug(f"Getting last VMID for node: {node_name}")

        try:
            last_vmid = self.database_session.exec(
                select(Nuage.vmid)
                .where(Nuage.node_name == node_name)
                .order_by(Nuage.vmid.desc())
            ).first()

            result_vmid = last_vmid if last_vmid else default_vmid

            if last_vmid:
                logger.info(f"Last VMID for node '{node_name}': {last_vmid}")
            else:
                logger.info(
                    f"No VMIDs found for node '{node_name}', using default: {default_vmid}"
                )

            return result_vmid

        except Exception as e:
            logger.error(f"Error retrieving last VMID for node '{node_name}': {str(e)}")
            raise
