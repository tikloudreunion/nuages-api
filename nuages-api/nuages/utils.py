from fastapi import Depends
from sqlmodel import Session

from ..database import get_session
from .repository import NuageRepository
from .service import NuageService


def get_nuage_service(session: Session = Depends(get_session)) -> NuageService:
    """Dependency to get NuageService instance."""
    repository = NuageRepository(session)
    return NuageService(repository)