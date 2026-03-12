




from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String

from models.base import MusicBase, SoftDeleteMixin, TimestampMixin


class Comment(MusicBase, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content: str = Column(String(255))
    creater_id: int = Column(Integer)
    song_id: int = Column(Integer, ForeignKey("songs.id", name="fk_comments_song_id"))

    @property
    def create_time(self) -> datetime:
        return self.created_at

    @property
    def update_time(self) -> datetime:
        return self.updated_at


class CommentIn(BaseModel):
    content: str
    song_id: int


class CommentOut(BaseModel):
    id: int
    content: str
    creater_id: int
    song_id: int
    create_time: datetime
    update_time: datetime
    delete_time: Optional[datetime] = None