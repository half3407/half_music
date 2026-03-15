from fastapi import Query
from pydantic import BaseModel, Field, model_validator
from config import settings

class PaginationParams(BaseModel):
    page: int = Field(default=settings.page_default,
                      ge=1,
                      description="页码（≥1）")
    page_size: int = Field(
        default=settings.page_size_default,
        ge=settings.page_size_min,
        le=settings.page_size_max,
        description=f"每页数量（{settings.page_size_min}-{settings.page_size_max}）"
    )


    @model_validator(mode='after')
    def validate_page_size(self):
        self.page_size = max(self.page_size, settings.page_size_min)
        self.page_size = min(self.page_size, settings.page_size_max)
        return self

def get_pagination(
    page: int = Query(
        default=settings.page_default,
        ge=1,
        description="页码"
    ),
    page_size: int = Query(
        default=settings.page_size_default,
        ge=settings.page_size_min,
        le=settings.page_size_max,
        description="每页数量"
    )
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)