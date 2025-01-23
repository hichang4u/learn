from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class PlatformBase(BaseModel):
    """플랫폼 기본 스키마"""
    name: str
    url: str
    logo: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

class PlatformCreate(PlatformBase):
    """플랫폼 생성 스키마"""
    pass

class PlatformUpdate(PlatformBase):
    """플랫폼 수정 스키마"""
    name: Optional[str] = None
    url: Optional[str] = None

class PlatformResponse(PlatformBase):
    """플랫폼 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 