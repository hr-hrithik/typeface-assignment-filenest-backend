import logging
import asyncio
from typing import Optional

from fastapi import UploadFile
from google.cloud.storage import Client
from google.auth import default as google_default_auth

from app.schemas.common_schemas import ResumableUploadSessionData

logger = logging.getLogger(__name__)

def get_gcs_client():
    credentials, _ = google_default_auth()
    gcs_client = Client(credentials=credentials)
    return gcs_client
    

async def upload_file_to_gcs(bucket_name: str, blob_to_upload: UploadFile, blob_file_path: str, timeout: int = 60):
    logs_prefix = ""
    blob_gcs_public_url = None
    
    try:
        gcs_client = get_gcs_client()
        bucket = gcs_client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(blob_name=blob_file_path)
        
        await blob_to_upload.seek(0)
        blob_string_data = await blob_to_upload.read()
        await asyncio.to_thread(lambda: blob.upload_from_string(data=blob_string_data, timeout=timeout))
        blob_gcs_public_url = blob.public_url
        
    except Exception as e:
        logger.exception(f"{logs_prefix} :: ERROR IN UPLOADING TO GCS :: {e}")
        
    return blob_gcs_public_url

async def create_resumable_upload_session(bucket_name: str, blob_name: str, origin: str, file_id: Optional[str] = None):
    logs_prefix = ""
    resumable_upload_session_data = ResumableUploadSessionData(
        file_id=file_id,
        blob_name=blob_name,
        session_url=None,
        public_url=None
    )

    try:
        gcs_client = get_gcs_client()
        bucket = gcs_client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(blob_name=blob_name)
        resumable_upload_session_data.session_url = await asyncio.to_thread(lambda: blob.create_resumable_upload_session(origin=origin))
        resumable_upload_session_data.public_url = blob.public_url
        
    except Exception as e:
        logger.exception(f"{logs_prefix} :: ERROR IN CREATING RESUMABLE UPLOAD URL :: {e}")
        
    return resumable_upload_session_data


async def download_gcs_file_as_bytes(bucket_name: str, blob_name: str):
    logs_prefix = ""
    file_bytes = None
    
    try:
        gcs_client = get_gcs_client()
        bucket = gcs_client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(blob_name=blob_name)
        
        if blob.exists():
            file_bytes = blob.download_as_bytes()
        
    except Exception as e:
        logger.exception(f"{logs_prefix} :: ERROR IN DOWNLOADING GCS FILE :: {e}")
        
    return file_bytes
    