from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from models.base import MusicBase, SoftDeleteMixin, TimestampMixin


class User(MusicBase, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(255))
    password_hash: str = Column(String(255))


class UserIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    user_name: str
    password: str
    create_time: datetime
    update_time: datetime
    delete_time: Optional[datetime] = None
