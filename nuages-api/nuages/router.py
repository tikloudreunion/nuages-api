from typing import List

from fastapi import routing, status, Depends

from .schemas import NuageResponse, CreateNuage, UpdateNuage, NuageStatus
from .service import NuageService
from .utils import get_nuage_service

router = routing.APIRouter()

@router.post(
    "",
    response_model=NuageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new nuage",
    description="Create a new nuage with the specified configuration.",
)
def create_nuage(
    nuage_data: CreateNuage, service: NuageService = Depends(get_nuage_service)
):
    """Create a new nuage."""
    return service.create_nuage(nuage_data)


@router.get(
    "",
    response_model=List[NuageResponse],
    status_code=status.HTTP_200_OK,
    summary="List all nuages",
    description="Retrieve a list of all .nuages.",
)
def list_nuages(service: NuageService = Depends(get_nuage_service)):
    """List all .nuages."""
    return service.list_nuages()


@router.get(
    "/{nuage_uuid}",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a nuage by UUID",
    description="Retrieve a specific nuage by its UUID.",
)
def get_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Get a specific nuage by its UUID."""
    return service.get_nuage(nuage_uuid)


@router.put(
    "/{nuage_uuid}",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a nuage",
    description="Update an existing nuage's configuration.",
)
def update_nuage(
    nuage_uuid: str,
    update_data: UpdateNuage,
    service: NuageService = Depends(get_nuage_service),
):
    """Update an existing nuage."""
    return service.update_nuage(nuage_uuid, update_data)

@router.put(
    "/{nuage_uuid}/start",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate a nuage",
    description="Activate a specific nuage by its UUID.",
)
def start_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Activate a specific nuage by its UUID."""
    return service.start_nuage(nuage_uuid)

@router.put(
    "/{nuage_uuid}/stop",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Stop a nuage",
    description="Stop a specific nuage by its UUID.",
)
def stop_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Stop a specific nuage by its UUID."""
    return service.stop_nuage(nuage_uuid)

@router.put(
    "/{nuage_uuid}/restart",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Restart a nuage",
    description="Restart a specific nuage by its UUID.",
)
def restart_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Restart a specific nuage by its UUID."""
    return service.restart_nuage(nuage_uuid)

@router.get(
    "/{nuage_uuid}/status",
    response_model=NuageStatus,
    status_code=status.HTTP_200_OK,
    summary="Get nuage status",
    description="Retrieve the status of a specific nuage by its UUID.",
)
def get_nuage_status(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Get the status of a specific nuage by its UUID."""
    return service.get_nuage_status(nuage_uuid)

@router.delete(
    "/{nuage_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a nuage",
    description="Delete a specific nuage by its UUID.",
)
def delete_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Delete a specific nuage by its UUID."""
    service.delete_nuage(nuage_uuid)
