from pydantic import BaseModel, HttpUrl
from typing import Optional

class ExtractRequest(BaseModel):
    url: HttpUrl

class VideoData(BaseModel):
    video_url: str
    title: Optional[str] = None
    size: Optional[int] = None
    type: Optional[str] = None
    warning: Optional[str] = None

class ExtractResponse(BaseModel):
    success: bool
    data: Optional[VideoData] = None
    error: Optional[str] = None
    message: Optional[str] = None
