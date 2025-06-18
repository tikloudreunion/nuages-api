import uuid

from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException

engine = create_engine("sqlite:///development.sqlite3")


class Nuage(SQLModel, table=True):
    uuid: str = Field(
        nullable=False,
        default=uuid.uuid4(),
        primary_key=True,
        description="Unique identifier for the nuage",
    )
    name: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="Name of the nuage, must be unique",
    )
    template: str = Field(nullable=False, description="Template used for the nuage")
    core: int = Field(nullable=False, default=1, description="Core count of the nuage")
    memory: int = Field(
        nullable=False, default=512, description="Memory size in MB of the nuage"
    )
    swap: int = Field(
        nullable=False, default=512, description="Swap size in MB of the nuage"
    )
    disk: int = Field(
        nullable=False, default=10240, description="Disk size in MB of the nuage"
    )


SQLModel.metadata.create_all(engine)


class CreateNuage(BaseModel):
    """
    Schema for creating a new nuage.
    """

    name: str
    template: str
    core: int = 1
    memory: int = 512
    swap: int = 512
    disk: int = 10240


class UpdateNuage(BaseModel):
    """
    Schema for updating an existing nuage.
    """

    core: int = 1
    memory: int = 512
    swap: int = 512
    disk: int = 10240


fastapi_application = FastAPI()


@fastapi_application.post("/", response_model=Nuage, status_code=status.HTTP_201_CREATED)
def create_nuage(nuage: CreateNuage):
    """
    Create a new nuage.
    """

    with Session(engine) as session:
        existing_nuage = session.exec(
            select(Nuage).where(Nuage.name == nuage.name)
        ).first()
        if existing_nuage:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A nuage with this name already exists.",
            )

        new_nuage = Nuage(
            uuid=uuid.uuid4().hex,
            name=nuage.name,
            template=nuage.template,
            core=nuage.core,
            memory=nuage.memory,
            swap=nuage.swap,
            disk=nuage.disk,
        )

        session.add(new_nuage)
        session.commit()
        session.refresh(new_nuage)

    return new_nuage


@fastapi_application.get("/", response_model=list[Nuage], status_code=status.HTTP_200_OK)
def list_nuages():
    """
    List all nuages.
    """
    with Session(engine) as session:
        nuages = session.exec(select(Nuage)).all()
    return nuages


@fastapi_application.get("/{nuage_uuid}", response_model=Nuage, status_code=status.HTTP_200_OK)
def get_nuage(nuage_uuid: str):
    """
    Get a specific nuage by its UUID.
    """
    with Session(engine) as session:
        existing_nuage = session.exec(
            select(Nuage).where(Nuage.uuid == nuage_uuid)
        ).first()
        if existing_nuage is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nuage not found.",
            )
    return existing_nuage


@fastapi_application.put("/{nuage_uuid}", response_model=Nuage, status_code=status.HTTP_200_OK)
def update_nuage(nuage_uuid: str, nuage: UpdateNuage):
    """
    Update an existing nuage.
    """
    with Session(engine) as session:
        existing_nuage = session.exec(
            select(Nuage).where(Nuage.uuid == nuage_uuid)
        ).first()
        if existing_nuage is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nuage not found.",
            )

        existing_nuage.core = nuage.core
        existing_nuage.memory = nuage.memory
        existing_nuage.swap = nuage.swap
        existing_nuage.disk = nuage.disk

        session.add(existing_nuage)
        session.commit()
        session.refresh(existing_nuage)

    return existing_nuage


@fastapi_application.delete("/{nuage_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nuage(nuage_uuid: str):
    """
    Delete a specific nuage by its UUID.
    """
    with Session(engine) as session:
        existing_nuage = session.exec(
            select(Nuage).where(Nuage.uuid == nuage_uuid)
        ).first()
        if existing_nuage is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nuage not found.",
            )

        session.delete(existing_nuage)
        session.commit()
