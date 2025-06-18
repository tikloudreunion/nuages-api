from fastapi import Depends
from sqlmodel import Session

from ..database import get_database_session
from .repository import NuageRepository
from .service import NuageService
from ..proxmox import get_proxmox_session, ProxmoxSession


def get_nuage_service(
    database_session: Session = Depends(get_database_session),
    proxmox_session: ProxmoxSession = Depends(get_proxmox_session),
) -> NuageService:
    """Dependency to get NuageService instance."""
    repository = NuageRepository(database_session)
    return NuageService(repository, proxmox_session)
