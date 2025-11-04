from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import ConfigDict

class Category(str, Enum):
    mekanik = "mekanik"
    elektrik = "elektrik"
    proses = "proses"
    diger = "diger"

class DefectBase(SQLModel):
    title: str
    description: Optional[str] = None
    category: Optional[Category] = None

class Defect(DefectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)

class DefectUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None
    status: Optional[str] = None

class Audit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    actor: str
    action: str
    endpoint: str
    method: str
    target_id: Optional[int] = None
    payload: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)

