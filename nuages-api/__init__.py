from .application import Application
from .nuages.router import router as nuages_router

application = Application()

application.include_router(nuages_router, prefix="/nuages", tags=["nuages"])