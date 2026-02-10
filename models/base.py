from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class MusicBase(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class TimestampMixin:
    """自动添加创建时间和更新时间"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),  # 数据库层面默认值
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # 更新时自动更新
        nullable=False,
        comment="更新时间"
    )


class SoftDeleteMixin:
    """软删除支持"""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="删除时间（NULL表示未删除）"
    )
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
