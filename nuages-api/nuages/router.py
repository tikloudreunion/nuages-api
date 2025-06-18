import logging
from typing import List

from fastapi import routing, status, Depends, Request

from .schemas import NuageResponse, CreateNuageRequest, NuageStatus
from .service import NuageService
from .utils import get_nuage_service

# Set up logger for this module
logger = logging.getLogger(__name__)

router = routing.APIRouter()


@router.post(
    "",
    response_model=NuageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new nuage",
    description="Create a new nuage with the specified configuration.",
)
def create_nuage(
    nuage_data: CreateNuageRequest,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Create a new nuage."""
    client_ip = request.client.host if request else "unknown"
    logger.info(
        f"POST /nuages - Creating nuage '{nuage_data.name}' from IP: {client_ip}"
    )
    logger.debug(f"Nuage creation request data: {nuage_data}")

    try:
        result = service.create_nuage(nuage_data)
        logger.info(
            f"Successfully created nuage '{result.name}' with UUID: {result.uuid}"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create nuage '{nuage_data.name}': {str(e)}")
        raise


@router.get(
    "",
    response_model=List[NuageResponse],
    status_code=status.HTTP_200_OK,
    summary="List all nuages",
    description="Retrieve a list of all nuages.",
)
def list_nuages(
    service: NuageService = Depends(get_nuage_service), request: Request = None
):
    """List all nuages."""
    client_ip = request.client.host if request else "unknown"
    logger.info(f"GET /nuages - Listing all nuages from IP: {client_ip}")

    try:
        nuages = service.list_nuages()
        logger.info(f"Successfully retrieved {len(nuages)} nuages")
        logger.debug(f"Retrieved nuages: {[nuage.name for nuage in nuages]}")
        return nuages
    except Exception as e:
        logger.error(f"Failed to list nuages: {str(e)}")
        raise


@router.get(
    "/{nuage_uuid}",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a nuage by UUID",
    description="Retrieve a specific nuage by its UUID.",
)
def get_nuage(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Get a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(f"GET /nuages/{nuage_uuid} - Retrieving nuage from IP: {client_ip}")

    try:
        nuage = service.get_nuage(nuage_uuid)
        logger.info(f"Successfully retrieved nuage '{nuage.name}' (UUID: {nuage_uuid})")
        return nuage
    except Exception as e:
        logger.error(f"Failed to retrieve nuage with UUID {nuage_uuid}: {str(e)}")
        raise


@router.put(
    "/{nuage_uuid}/start",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate a nuage",
    description="Activate a specific nuage by its UUID.",
)
def start_nuage(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Activate a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(f"PUT /nuages/{nuage_uuid}/start - Starting nuage from IP: {client_ip}")

    try:
        result = service.start_nuage(nuage_uuid)
        logger.info(f"Successfully started nuage '{result.name}' (UUID: {nuage_uuid})")
        return result
    except Exception as e:
        logger.error(f"Failed to start nuage with UUID {nuage_uuid}: {str(e)}")
        raise


@router.put(
    "/{nuage_uuid}/stop",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Stop a nuage",
    description="Stop a specific nuage by its UUID.",
)
def stop_nuage(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Stop a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(f"PUT /nuages/{nuage_uuid}/stop - Stopping nuage from IP: {client_ip}")

    try:
        result = service.stop_nuage(nuage_uuid)
        logger.info(f"Successfully stopped nuage '{result.name}' (UUID: {nuage_uuid})")
        return result
    except Exception as e:
        logger.error(f"Failed to stop nuage with UUID {nuage_uuid}: {str(e)}")
        raise


@router.put(
    "/{nuage_uuid}/reboot",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reboot a nuage",
    description="Reboot a specific nuage by its UUID.",
)
def reboot_nuage(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Reboot a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(
        f"PUT /nuages/{nuage_uuid}/reboot - Rebooting nuage from IP: {client_ip}"
    )

    try:
        result = service.reboot_nuage(nuage_uuid)
        logger.info(f"Successfully rebooted nuage '{result.name}' (UUID: {nuage_uuid})")
        return result
    except Exception as e:
        logger.error(f"Failed to reboot nuage with UUID {nuage_uuid}: {str(e)}")
        raise


@router.get(
    "/{nuage_uuid}/status",
    response_model=NuageStatus,
    status_code=status.HTTP_200_OK,
    summary="Get nuage status",
    description="Retrieve the status of a specific nuage by its UUID.",
)
def get_nuage_status(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Get the status of a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(
        f"GET /nuages/{nuage_uuid}/status - Getting nuage status from IP: {client_ip}"
    )

    try:
        status_info = service.get_nuage_status(nuage_uuid)
        logger.info(
            f"Successfully retrieved status for nuage UUID {nuage_uuid}: {status_info.status}"
        )
        logger.debug(f"Nuage status details: {status_info}")
        return status_info
    except Exception as e:
        logger.error(f"Failed to get status for nuage with UUID {nuage_uuid}: {str(e)}")
        raise


@router.delete(
    "/{nuage_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a nuage",
    description="Delete a specific nuage by its UUID.",
)
def delete_nuage(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Delete a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(f"DELETE /nuages/{nuage_uuid} - Deleting nuage from IP: {client_ip}")

    try:
        service.delete_nuage(nuage_uuid)
        logger.info(f"Successfully deleted nuage with UUID: {nuage_uuid}")
    except Exception as e:
        logger.error(f"Failed to delete nuage with UUID {nuage_uuid}: {str(e)}")
        raise


@router.put(
    "/{nuage_uuid}/shutdown",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Shutdown a nuage",
    description="Shutdown a specific nuage by its UUID.",
)
def shutdown_nuage(
    nuage_uuid: str,
    service: NuageService = Depends(get_nuage_service),
    request: Request = None,
):
    """Shutdown a specific nuage by its UUID."""
    client_ip = request.client.host if request else "unknown"
    logger.info(
        f"PUT /nuages/{nuage_uuid}/shutdown - Shutting down nuage from IP: {client_ip}"
    )

    try:
        result = service.shutdown_nuage(nuage_uuid)
        logger.info(f"Successfully shutdown nuage '{result.name}' (UUID: {nuage_uuid})")
        return result
    except Exception as e:
        logger.error(f"Failed to shutdown nuage with UUID {nuage_uuid}: {str(e)}")
        raise
