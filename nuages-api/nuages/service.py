from typing import List
import random

from fastapi import HTTPException, status

from .models import Nuage
<<<<<<< HEAD
from .schemas import CreateNuage, UpdateNuage, NuageStatus
=======
from .schemas import CreateNuageRequest, CreateNuage
>>>>>>> main
from .repository import NuageRepository
from ..proxmox import ProxmoxSession


class NuageService:
    """Service class for Nuage business logic."""

    def __init__(self, repository: NuageRepository, proxmox_session: ProxmoxSession):
        self.repository = repository
        self.proxmox_session = proxmox_session

    def create_nuage(self, nuage_data: CreateNuageRequest) -> Nuage:
        """Create a new nuage with validation."""
        existing_nuage = self.repository.get_by_name(nuage_data.name)
        if existing_nuage:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A nuage with name '{nuage_data.name}' already exists.",
            )

        try:
            nodes = self.proxmox_session.nodes.get()  # type: ignore
        except Exception as execption:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Proxmox: {str(execption)}",
            )

        node_names = [node_name["node"] for node_name in nodes]  # type: ignore

        node_name = random.choice(node_names)  # type: ignore

        # Find the last VMID in the database with the same node_name
        try:
            last_vmid = self.repository.get_last_vmid_by_node_name(node_name)  # type: ignore
        except Exception as execption:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to retrieve last VMID: {str(execption)}",
            )
        vmid = last_vmid + 1

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
            )
        except Exception as execption:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to create LXC in Proxmox: {str(execption)}",
            )

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

        return self.repository.create(nuage)

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

    def delete_nuage(self, nuage_uuid: str) -> None:
        """Delete a nuage."""
        nuage = self.get_nuage(nuage_uuid)
        self.repository.delete(nuage)

    def start_nuage(self, nuage_uuid: str) -> Nuage:
        """Start a nuage."""
        pass

    def stop_nuage(self, nuage_uuid: str) -> Nuage:
        """Stop a nuage."""
        nuage = self.get_nuage(nuage_uuid)
        try:
            self.proxmox_session.nodes(nuage.node_name).lxc(nuage.vmid).status.stop.create()  # type: ignore
        except Exception as execption:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to stop LXC in Proxmox: {str(execption)}",
            )
        return nuage

    def restart_nuage(self, nuage_uuid: str) -> Nuage:
        """Restart a nuage."""
        self.stop_nuage(nuage_uuid)
        return self.start_nuage(nuage_uuid)
