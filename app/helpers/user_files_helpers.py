import asyncio
import uuid
import logging
import pillow_avif

from io import BytesIO
from fastapi import UploadFile
from PIL import Image, ImageOps

from app.config.settings import get_settings
from app.constants.user_files_constants import DEFAULT_THUMBNAILS, MIME_TYPE_FILE_TYPE_MAPPING
from app.database.db_enums_classes import UserFilesFileType
from app.gcp.gcp_helpers import create_resumable_upload_session, upload_file_to_gcs
from app.schemas.common_schemas import ResumableUploadSessionData

settings = get_settings()
logger = logging.getLogger(__name__)

def generate_thumbnail_from_image_blob_data(image_data ):
    with Image.open(BytesIO(image_data)) as img:
        image_format = img.format
        temp_exif_img = ImageOps.exif_transpose(img)
        
        img = temp_exif_img
        width, height = img.size
        aspect_ratio = width / height
        
        thumbnail_width = int(min(256, width))
        thumbnail_height = int(thumbnail_width / aspect_ratio)
        
        thumbnail_img = img.resize((thumbnail_width, thumbnail_height))
        thumbnail_img_bytes = BytesIO()
        
        thumbnail_img.save(thumbnail_img_bytes, format=image_format)
        
        return UploadFile(file=BytesIO(thumbnail_img_bytes.getvalue()))
        
        
        

def get_file_type_from_mime_type(mime_type: str):
    return MIME_TYPE_FILE_TYPE_MAPPING.get(mime_type, UserFilesFileType.OTHERS.value)

async def get_file_thumbnail_url(file_type: str, user_id: str = None, file: UploadFile = None):
    thumbnail_url = DEFAULT_THUMBNAILS.get(file_type)
    
    try:
        if file_type == UserFilesFileType.IMAGE.value and user_id and file:
            await file.seek(0)
            file_data = await file.read()
            thumbnail_blob = generate_thumbnail_from_image_blob_data(image_data=file_data)
            thumbnail_blob_name = f"{user_id}/thumbnails/{uuid.uuid4().hex}_{file.filename}"
            
            thumbnail_url = await upload_file_to_gcs(bucket_name=settings.gcs_bucket_name, blob_to_upload=thumbnail_blob, blob_file_path=thumbnail_blob_name)
        
    except Exception as e:
        logger.exception(f"ERROR IN GENERATING THUMBNAIL URL :: {e}")
    
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