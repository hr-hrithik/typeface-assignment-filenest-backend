import asyncio
from fastapi import UploadFile
from app.config.settings import get_settings
from app.constants.user_files_constants import DEFAULT_THUMBNAILS, MIME_TYPE_FILE_TYPE_MAPPING
from app.database.db_enums_classes import UserFilesFileType
from app.gcp.gcp_helpers import create_resumable_upload_session
from app.schemas.common_schemas import ResumableUploadSessionData

settings = get_settings()

def get_file_type_from_mime_type(mime_type: str):
    return MIME_TYPE_FILE_TYPE_MAPPING.get(mime_type, UserFilesFileType.OTHERS.value)

async def get_file_thumbnail_url(file_type: str, file: UploadFile = None):
    thumbnail_url = DEFAULT_THUMBNAILS.get(file_type)
    
    return thumbnail_url

async def create_resumable_upload_session_data_mapping(file_id_blob_name_mapping: dict[str, str], origin: str) -> dict[str, ResumableUploadSessionData]:
    file_id_resumable_upload_session_data_mapping = {}
    coroutines_list = []
    
    for file_id, blob_name in file_id_blob_name_mapping.items():
        coroutines_list.append(asyncio.create_task(create_resumable_upload_session(bucket_name=settings.gcs_bucket_name, blob_name=blob_name, origin=origin, file_id=file_id)))
    
    response = await asyncio.gather(*coroutines_list)
    
    for item in response:
        if type(item.file_id) is str:
            file_id_resumable_upload_session_data_mapping[item.file_id] = item
    
    return file_id_resumable_upload_session_data_mapping