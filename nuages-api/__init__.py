from dotenv import load_dotenv

from .application import Application
from .nuages.router import router as nuages_router

load_dotenv()

application = Application()

application.include_router(nuages_router, prefix="/nuages", tags=["nuages"])