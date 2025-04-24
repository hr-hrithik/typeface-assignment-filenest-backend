import datetime
from typing import List
from pydantic import BaseModel

##REQUEST SCHEMAS
class RequestFileMetadata(BaseModel):
    file_request_id: str
    file_name: str
    file_size: float
    mime_type: str
    file_modified_at: int

class UserFilesResumableUploadRequest(BaseModel):
    user_id: str
    folder_id: str
    files: List[RequestFileMetadata]
    
class FileUploadSuccessRequest(BaseModel):
    user_id: str
    folder_id: str
    file_id: str


##RESPONSE SCHEMAS
class UserFileMetadata(BaseModel):
    file_id: str
    file_name: str
    file_type: str
    file_public_url: str
    file_last_modified: datetime.datetime = None

class GetUserFilesResponse(BaseModel):
    files: List[UserFileMetadata] = []
    is_next_page_available: bool = False

class ResumableUploadResponseFileData(BaseModel):
    file_id: str
    file_name: str
    file_size: int
    file_upload_status: str
    resumable_upload_url: str
    
class UserFilesResumableUploadResponse(BaseModel):
    files: dict[str, ResumableUploadResponseFileData]
    
class UserFolderContentMetadata(BaseModel):
    content_type: str
    content_id: str
    content_name: str
    content_size: float
    content_last_modified: datetime.datetime
    content_file_type: str
    content_thumbnail_url: str
    
class UserFolderContentsResponse(BaseModel):
    folder_content_count: int = 0
    folder_name: str
    folder_size: float
    folder_last_modified: datetime.datetime
    folder_content: List[UserFolderContentMetadata]
    
class UserFileDetails(BaseModel):
    file_name: str
    file_type: str
    file_size: float
    file_public_url: str
    file_thumbnail_url: str
    file_last_modified: datetime.datetime