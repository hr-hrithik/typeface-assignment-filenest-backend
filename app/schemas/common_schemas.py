from typing import Any, Optional
from pydantic import BaseModel

from app.constants.common_constants import API_STATUS_STRINGS


class APIResponse(BaseModel):
    status: str = API_STATUS_STRINGS.OK.value
    status_code: int = 200
    data: dict[str, Any] = {}
    
class APIErrorMessage(BaseModel):
    message: str = 'An unexpected error occured'
    
class ResumableUploadSessionData(BaseModel):
    file_id: Optional[str] = None
    blob_name: Optional[str] = None
    session_url: Optional[str] = None
    public_url: Optional[str] = None