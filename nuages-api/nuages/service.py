import logging
from typing import List
import random

from fastapi import HTTPException, status

from .models import Nuage
from .schemas import CreateNuageRequest, CreateNuage, NuageStatus
from .repository import NuageRepository
from ..proxmox import ProxmoxSession

# Set up logger for this module
logger = logging.getLogger(__name__)


def safe_percentage(used: float, total: float) -> float:
    """Calculate percentage safely, avoiding division by zero."""
    return abs(used * 100.0 / total) if total > 0 else 0.0


class NuageService:
    """Service class for Nuage business logic."""

    def __init__(self, repository: NuageRepository, proxmox_session: ProxmoxSession):
        self.repository = repository
        self.proxmox_session = proxmox_session
        logger.info("NuageService initialized")

    def create_nuage(self, nuage_data: CreateNuageRequest) -> Nuage:
        """Create a new nuage with validation."""
        logger.info(f"Starting nuage creation process for: {nuage_data.name}")
        logger.debug(f"Nuage creation request: {nuage_data}")

        # Check for existing nuage
        logger.debug(f"Checking if nuage with name '{nuage_data.name}' already exists")
        existing_nuage = self.repository.get_by_name(nuage_data.name)
        if existing_nuage:
            logger.warning(f"Nuage creation failed: '{nuage_data.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A nuage with name '{nuage_data.name}' already exists.",
            )

        # Get available Proxmox nodes
        logger.debug("Retrieving available Proxmox nodes")
        try:
            nodes = self.proxmox_session.nodes.get()  # type: ignore
            logger.info(f"Successfully retrieved {len(nodes)} Proxmox nodes")  # type: ignore
        except Exception as exception:
            logger.error(f"Failed to connect to Proxmox: {str(exception)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Proxmox: {str(exception)}",
            )

        node_names = [node_name["node"] for node_name in nodes]  # type: ignore
        node_name = random.choice(node_names)  # type: ignore
        logger.info(f"Selected node '{node_name}' for nuage creation")

        # Find the next available VMID globally (not per node)
        logger.debug("Retrieving next available VMID globally")
        try:
            # Proxmox API: /cluster/nextid gives the next available VMID
            vmid = int(self.proxmox_session.cluster.nextid.get())
            logger.info(f"Assigned global VMID {vmid} to new nuage")
        except Exception as exception:
            logger.error(
                f"Failed to retrieve next available VMID from Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to retrieve next available VMID: {str(exception)}",
            )

        # Create LXC container in Proxmox
        logger.info(f"Creating LXC container on node '{node_name}' with VMID {vmid}")
        logger.debug(
            f"LXC creation parameters: template={nuage_data.template}, memory={nuage_data.memory}, "
            f"cores={nuage_data.cores}, disk={nuage_data.disk}"
        )
        try:
            lxc = self.proxmox_session.nodes(node_name).lxc.create(  # type: ignore
                vmid=vmid,
                ostemplate=nuage_data.template,
                memory=nuage_data.memory,
                swap=nuage_data.swap,
                cores=nuage_data.cores,
                hostname=f"{nuage_data.name}.tikloud.re",
                storage="local-lvm",
                start=1,  # Automatically start the LXC after creation
                rootfs=f"local-lvm:{nuage_data.disk}",
                password="rootroot",
            )
            logger.info(
                f"Successfully created LXC container for nuage '{nuage_data.name}' on Proxmox"
            )
        except Exception as exception:
            logger.error(
                f"Failed to create LXC container for '{nuage_data.name}' on Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to create LXC in Proxmox: {str(exception)}",
            )

        # Create nuage record in database
        logger.debug("Creating nuage record in database")
        nuage = CreateNuage(
            name=nuage_data.name,
            node_name=node_name,  # type: ignore
            template=nuage_data.template,
            cores=nuage_data.cores,
            memory=nuage_data.memory,
            swap=nuage_data.swap,
            disk=nuage_data.disk,
            vmid=vmid,
        )

        try:
            created_nuage = self.repository.create(nuage)
            logger.info(
                f"Successfully created nuage '{created_nuage.name}' with UUID: {created_nuage.uuid}"
            )
            return created_nuage
        except Exception as exception:
            logger.error(
                f"Failed to save nuage '{nuage_data.name}' to database: {str(exception)}"
            )
            # Note: At this point, the LXC exists in Proxmox but not in our database
            # Consider implementing cleanup logic here
            raise

    def get_nuage(self, nuage_uuid: str) -> Nuage:
        """Get a nuage by UUID."""
        logger.debug(f"Retrieving nuage with UUID: {nuage_uuid}")
        nuage = self.repository.get_by_uuid(nuage_uuid)
        if not nuage:
            logger.warning(f"Nuage not found with UUID: {nuage_uuid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nuage with UUID '{nuage_uuid}' not found.",
            )
        logger.debug(f"Found nuage '{nuage.name}' for UUID: {nuage_uuid}")
        return nuage

    def list_nuages(self) -> List[Nuage]:
        """List all nuages."""
        logger.debug("Retrieving all nuages")
        nuages = self.repository.get_all()
        logger.info(f"Retrieved {len(nuages)} nuages")
        return nuages

    def get_nuage_status(self, nuage_uuid: str) -> NuageStatus:
        """Get the status of a nuage."""
        logger.info(f"Getting status for nuage UUID: {nuage_uuid}")

        nuage = self.get_nuage(nuage_uuid)
        logger.debug(
            f"Retrieved nuage '{nuage.name}' on node '{nuage.node_name}' with VMID {nuage.vmid}"
        )

        try:
            logger.debug(
                f"Querying Proxmox for LXC status: node={nuage.node_name}, vmid={nuage.vmid}"
            )
            nuage_status = self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).status.current.get()  # type: ignore
            logger.debug(f"Raw Proxmox status response: {nuage_status}")

            status_info = NuageStatus(
                status=nuage_status["status"],  # type: ignore
                message="No additional message available.",  # type: ignore
                cpu_usage=abs(nuage_status.get("cpu", 0)),  # type: ignore
                memory_usage=safe_percentage(nuage_status.get("mem", 0), nuage_status.get("maxmem", 0)),  # type: ignore
                disk_usage=safe_percentage(nuage_status.get("disk", 0), nuage_status.get("maxdisk", 0)),  # type: ignore
                swap_usage=safe_percentage(nuage_status.get("swap", 0), nuage_status.get("maxswap", 0)),  # type: ignore
            )

            logger.info(
                f"Successfully retrieved status for nuage '{nuage.name}': {status_info.status}, "
                f"CPU: {status_info.cpu_usage:.1f}%, Memory: {status_info.memory_usage:.1f}%"
            )
            return status_info

        except Exception as exception:
            logger.error(
                f"Failed to retrieve LXC status from Proxmox for nuage '{nuage.name}': {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to retrieve LXC status from Proxmox: {str(exception)}",
            )

    def delete_nuage(self, nuage_uuid: str) -> None:
        """Delete a nuage."""
        logger.info(f"Starting deletion process for nuage UUID: {nuage_uuid}")

        nuage = self.get_nuage(nuage_uuid)
        logger.info(
            f"Deleting nuage '{nuage.name}' on node '{nuage.node_name}' with VMID {nuage.vmid}"
        )

        # Delete LXC from Proxmox first
        try:
            logger.debug(
                f"Deleting LXC container from Proxmox: node={nuage.node_name}, vmid={nuage.vmid}"
            )
            self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).delete(  # type: ignore
                force=1,  # Force deletion without confirmation
                purge=1,  # Purge the LXC
            )  # type: ignore
            logger.info(
                f"Successfully deleted LXC container for nuage '{nuage.name}' from Proxmox"
            )
        except Exception as exception:
            logger.error(
                f"Failed to delete LXC container for nuage '{nuage.name}' from Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to delete LXC in Proxmox: {str(exception)}",
            )

        # Delete nuage record from database
        try:
            self.repository.delete(nuage)
            logger.info(
                f"Successfully deleted nuage '{nuage.name}' with UUID: {nuage_uuid}"
            )
        except Exception as exception:
            logger.error(
                f"Failed to delete nuage '{nuage.name}' from database: {str(exception)}"
            )
            # Note: At this point, the LXC is deleted from Proxmox but the record remains in database
            raise

    def start_nuage(self, nuage_uuid: str) -> Nuage:
        """Start a nuage."""
        logger.info(f"Starting nuage with UUID: {nuage_uuid}")

        nuage = self.get_nuage(nuage_uuid)
        logger.info(
            f"Starting nuage '{nuage.name}' on node '{nuage.node_name}' with VMID {nuage.vmid}"
        )

        try:
            self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).status.start.create()  # type: ignore
            logger.info(f"Successfully started nuage '{nuage.name}'")
            return nuage
        except Exception as exception:
            logger.error(
                f"Failed to start nuage '{nuage.name}' on Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to start LXC in Proxmox: {str(exception)}",
            )

    def stop_nuage(self, nuage_uuid: str) -> Nuage:
        """Stop a nuage."""
        logger.info(f"Stopping nuage with UUID: {nuage_uuid}")

        nuage = self.get_nuage(nuage_uuid)
        logger.info(
            f"Stopping nuage '{nuage.name}' on node '{nuage.node_name}' with VMID {nuage.vmid}"
        )

        try:
            self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).status.stop.create()  # type: ignore
            logger.info(f"Successfully stopped nuage '{nuage.name}'")
            return nuage
        except Exception as exception:
            logger.error(
                f"Failed to stop nuage '{nuage.name}' on Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to stop LXC in Proxmox: {str(exception)}",
            )

    def reboot_nuage(self, nuage_uuid: str) -> Nuage:
        """Reboot a nuage."""
        logger.info(f"Rebooting nuage with UUID: {nuage_uuid}")

        nuage = self.get_nuage(nuage_uuid)
        logger.info(
            f"Rebooting nuage '{nuage.name}' on node '{nuage.node_name}' with VMID {nuage.vmid}"
        )

        try:
            self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).status.reboot.create()  # type: ignore
            logger.info(f"Successfully rebooted nuage '{nuage.name}'")
            return nuage
        except Exception as exception:
            logger.error(
                f"Failed to reboot nuage '{nuage.name}' on Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to reboot LXC in Proxmox: {str(exception)}",
            )

    def shutdown_nuage(self, nuage_uuid: str) -> Nuage:
        """Shutdown a nuage."""
        logger.info(f"Shutting down nuage with UUID: {nuage_uuid}")

        nuage = self.get_nuage(nuage_uuid)
        logger.info(
            f"Shutting down nuage '{nuage.name}' on node '{nuage.node_name}' with VMID {nuage.vmid}"
        )

        try:
            self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).status.shutdown.create()  # type: ignore
            logger.info(f"Successfully shut down nuage '{nuage.name}'")
            return nuage
        except Exception as exception:
            logger.error(
                f"Failed to shutdown nuage '{nuage.name}' on Proxmox: {str(exception)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to shutdown LXC in Proxmox: {str(exception)}",
            )
