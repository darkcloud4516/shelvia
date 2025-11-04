from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class Category(str, Enum):
    mekanik = "mekanik"
    elektrik = "elektrik"
    proses = "proses"
    diger = "diger"

class DefectBase(SQLModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    category: Optional[Category] = None

class Defect(DefectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="open")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class DefectUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=3)
    description: Optional[str] = None
    category: Optional[Category] = None
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None

class Audit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    actor: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    target_id: Optional[int] = None
    payload: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

