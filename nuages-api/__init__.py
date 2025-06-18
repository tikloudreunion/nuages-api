import uuid
from typing import List
from contextlib import contextmanager, asynccontextmanager

from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel, Field as PydanticField
from fastapi import FastAPI, status, HTTPException, Depends


# Database Configuration
DATABASE_URL = "sqlite:///development.sqlite3"
engine = create_engine(DATABASE_URL, echo=False)


# Database Models
class Nuage(SQLModel, table=True):
    """Database model for Nuage resources."""

    uuid: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        primary_key=True,
        description="Unique identifier for the nuage",
    )
    name: str = Field(
        unique=True,
        index=True,
        description="Name of the nuage, must be unique",
    )
    template: str = Field(description="Template used for the nuage")
    core: int = Field(default=1, ge=1, description="Core count of the nuage")
    memory: int = Field(default=512, ge=256, description="Memory size in MB")
    swap: int = Field(default=512, ge=0, description="Swap size in MB")
    disk: int = Field(default=10240, ge=1024, description="Disk size in MB")


# Pydantic Schemas
class NuageBase(BaseModel):
    """Base schema for Nuage with common fields."""

    name: str = PydanticField(..., min_length=1, max_length=255)
    template: str = PydanticField(..., min_length=1, max_length=255)
    core: int = PydanticField(default=1, ge=1, le=64)
    memory: int = PydanticField(default=512, ge=256, le=32768)
    swap: int = PydanticField(default=512, ge=0, le=16384)
    disk: int = PydanticField(default=10240, ge=1024, le=1048576)


class CreateNuage(NuageBase):
    """Schema for creating a new nuage."""

    pass


class UpdateNuage(BaseModel):
    """Schema for updating an existing nuage."""

    core: int = PydanticField(default=1, ge=1, le=64)
    memory: int = PydanticField(default=512, ge=256, le=32768)
    swap: int = PydanticField(default=512, ge=0, le=16384)
    disk: int = PydanticField(default=10240, ge=1024, le=1048576)


class NuageResponse(NuageBase):
    """Schema for nuage responses."""

    uuid: str


# Database Session Management
@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_session():
    """Dependency for FastAPI to get database session."""
    with get_db_session() as session:
        yield session


# Repository Layer
class NuageRepository:
    """Repository class for Nuage database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_uuid(self, nuage_uuid: str) -> Nuage | None:
        """Get a nuage by its UUID."""
        return self.session.exec(select(Nuage).where(Nuage.uuid == nuage_uuid)).first()

    def get_by_name(self, name: str) -> Nuage | None:
        """Get a nuage by its name."""
        return self.session.exec(select(Nuage).where(Nuage.name == name)).first()

    def get_all(self) -> List[Nuage]:
        """Get all nuages."""
        return list(self.session.exec(select(Nuage)))

    def create(self, nuage_data: CreateNuage) -> Nuage:
        """Create a new nuage."""
        nuage = Nuage(**nuage_data.model_dump())
        self.session.add(nuage)
        self.session.commit()
        self.session.refresh(nuage)
        return nuage

    def update(self, nuage: Nuage, update_data: UpdateNuage) -> Nuage:
        """Update an existing nuage."""
        for field, value in update_data.model_dump().items():
            setattr(nuage, field, value)

        self.session.add(nuage)
        self.session.commit()
        self.session.refresh(nuage)
        return nuage

    def delete(self, nuage: Nuage) -> None:
        """Delete a nuage."""
        self.session.delete(nuage)
        self.session.commit()


# Service Layer
class NuageService:
    """Service class for Nuage business logic."""

    def __init__(self, repository: NuageRepository):
        self.repository = repository

    def create_nuage(self, nuage_data: CreateNuage) -> Nuage:
        """Create a new nuage with validation."""
        existing_nuage = self.repository.get_by_name(nuage_data.name)
        if existing_nuage:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A nuage with name '{nuage_data.name}' already exists.",
            )

        return self.repository.create(nuage_data)

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

    def update_nuage(self, nuage_uuid: str, update_data: UpdateNuage) -> Nuage:
        """Update a nuage."""
        nuage = self.get_nuage(nuage_uuid)  # This will raise 404 if not found
        return self.repository.update(nuage, update_data)

    def delete_nuage(self, nuage_uuid: str) -> None:
        """Delete a nuage."""
        nuage = self.get_nuage(nuage_uuid)  # This will raise 404 if not found
        self.repository.delete(nuage)


# Dependency Functions
def get_nuage_service(session: Session = Depends(get_session)) -> NuageService:
    """Dependency to get NuageService instance."""
    repository = NuageRepository(session)
    return NuageService(repository)


# Initialize Database
def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context to initialize database on startup."""
    init_db()
    yield

app = FastAPI(
    title="Nuage Management API",
    description="API for managing Nuage resources",
    version="1.0.0",
    lifespan=lifespan,
)

# API Endpoints
@app.post(
    "/nuages/",
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


@app.get(
    "/nuages/",
    response_model=List[NuageResponse],
    status_code=status.HTTP_200_OK,
    summary="List all nuages",
    description="Retrieve a list of all nuages.",
)
def list_nuages(service: NuageService = Depends(get_nuage_service)):
    """List all nuages."""
    return service.list_nuages()


@app.get(
    "/nuages/{nuage_uuid}",
    response_model=NuageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a nuage by UUID",
    description="Retrieve a specific nuage by its UUID.",
)
def get_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Get a specific nuage by its UUID."""
    return service.get_nuage(nuage_uuid)


@app.put(
    "/nuages/{nuage_uuid}",
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


@app.delete(
    "/nuages/{nuage_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a nuage",
    description="Delete a specific nuage by its UUID.",
)
def delete_nuage(nuage_uuid: str, service: NuageService = Depends(get_nuage_service)):
    """Delete a specific nuage by its UUID."""
    service.delete_nuage(nuage_uuid)
