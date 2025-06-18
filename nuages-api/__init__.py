from dotenv import load_dotenv

from .application import Application
from .nuages.router import router as nuages_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

application = Application()

origins = ["*"]

application.include_router(nuages_router, prefix="/nuages", tags=["nuages"])
application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
