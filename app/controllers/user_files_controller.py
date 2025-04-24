import asyncio
import datetime
import io
import logging
import uuid

import app.crud.user_files_crud as user_files_crud

from typing import List
from fastapi import UploadFile
from sqlalchemy.orm.session import Session

from app.constants.common_constants import API_STATUS_STRINGS
from app.constants.user_files_constants import GET_USER_FILES_PAGE_SIZE
from app.crud.generic_crud import GenericCrud
from app.database.db_enums_classes import FolderContentsContentType, UserFilesUploadStatus
from app.database.models import UserFiles, UserProfile
from app.gcp.gcp_helpers import create_resumable_upload_session, download_gcs_file_as_bytes, upload_file_to_gcs
from app.helpers.user_files_helpers import create_resumable_upload_session_data_mapping, get_file_thumbnail_url, get_file_type_from_mime_type
from app.schemas.authentication_schemas import UserAuthentication
from app.schemas.common_schemas import APIErrorMessage, APIResponse
from app.schemas.user_files_schemas import FileUploadSuccessRequest, GetUserFilesResponse, ResumableUploadResponseFileData, UserFileDetails, UserFileMetadata, UserFilesResumableUploadRequest, UserFilesResumableUploadResponse, UserFolderContentMetadata, UserFolderContentsResponse
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def get_user_files_controller(user_id: str, page: int, db_session: Session):
    response = APIResponse()
    try:
        user_files = []
        offset = GET_USER_FILES_PAGE_SIZE * max(page - 1, 0)
        user_files_rows = GenericCrud.get_rows(table_model=UserFiles, query_conditions=[UserFiles.user_id == user_id], db_session=db_session,
                                               order_by=[UserFiles.updated_at.desc()], offset=offset, limit=GET_USER_FILES_PAGE_SIZE + 1)
        
        for file in user_files_rows[0: GET_USER_FILES_PAGE_SIZE]:
            user_files.append(UserFileMetadata(**file._asdict(), file_id=file.id))
            
        response.data = GetUserFilesResponse(files=user_files, is_next_page_available=len(user_files_rows) > GET_USER_FILES_PAGE_SIZE).model_dump(mode="json")
        
    except Exception as e:
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN GETTING USER FILES :: {e}")
    
    return response

async def upload_user_files_controller(user_id: str, folder_id: str, file_modified_at: int, user_file: UploadFile, db_session: Session):
    response = APIResponse()
    try:
        uploaded_files = None
        
        file_id = uuid.uuid4().hex
        file_type = get_file_type_from_mime_type(mime_type=user_file.content_type)
        file_name_without_spaces = user_file.filename.replace(' ', '_')
        file_blob_name = f'{user_id}/{file_id}_{file_name_without_spaces}'
        file_public_url = await upload_file_to_gcs(bucket_name=settings.gcs_bucket_name, blob_to_upload=user_file, blob_file_path=file_blob_name)
        file_thumbnail_url = await get_file_thumbnail_url(file_type=file_type, file=user_file)
        
        user_file_row_data = {
            "id": file_id,
            "user_id": user_id,
            "folder_id": folder_id,
            "file_name": user_file.filename,
            "file_type": file_type,
            "file_size": user_file.size,
            "file_public_url": file_public_url,
            "file_thumbnail_url": file_thumbnail_url,
            "file_last_modified": datetime.datetime.fromtimestamp(file_modified_at / 1000),
            "file_upload_status": UserFilesUploadStatus.OK.value,
            "file_blob_name": file_blob_name
        }
        
        user_files_crud.create_user_files_rows(files_row_data=[user_file_row_data], db_session=db_session, auto_commit=True)
        user_files_crud.create_folder_content_rows_for_files(files_row_data=[user_file_row_data], db_session=db_session, auto_commit=True)
        
        response.data = {
            "file": UserFileDetails(**user_file_row_data, file_id=user_file_row_data.get('id'))
        }
        
    except Exception as e:
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN UPLOADING USER FILES :: {e}")
    
    return response

async def user_files_resumable_upload_controller(data: UserFilesResumableUploadRequest, user_authentication: UserAuthentication, origin: str, db_session: Session):
    response = APIResponse()
    try:
        user_files_row_data = []
        user_files_response_data = {}
        file_id_blob_name_mapping = {}
        request_file_id_file_id_mapping = {}
        
        for file in data.files:
            file_id = uuid.uuid4().hex
            request_file_id_file_id_mapping[file.file_request_id] = file_id
            
            file_blob_name = f"{user_authentication.user_id}/{file_id}_{file.file_name}"
            file_id_blob_name_mapping[file_id] = file_blob_name
        
        file_id_resumable_upload_session_data_mapping = await create_resumable_upload_session_data_mapping(file_id_blob_name_mapping=file_id_blob_name_mapping, origin=origin)
        
        for file in data.files:
            if file.file_request_id not in request_file_id_file_id_mapping:
                continue
            
            file_id = request_file_id_file_id_mapping.get(file.file_request_id)
            file_type = get_file_type_from_mime_type(mime_type=file.mime_type)
            thumbnail_url = await get_file_thumbnail_url(file_type=file_type)
            file_blob_name = file_id_resumable_upload_session_data_mapping.get(file_id).blob_name
            file_resumable_upload_url = file_id_resumable_upload_session_data_mapping.get(file_id).session_url
            file_public_url = file_id_resumable_upload_session_data_mapping.get(file_id).public_url
            
            file_data = {
                "id": file_id,
                "user_id": user_authentication.user_id,
                "folder_id": data.folder_id,
                "file_name": file.file_name,
                "file_type": file_type,
                "file_size": file.file_size,
                "file_public_url": file_public_url,
                "file_thumbnail_url": thumbnail_url,
                "file_last_modified": datetime.datetime.fromtimestamp(file.file_modified_at / 1000),
                "file_upload_status": UserFilesUploadStatus.PENDING.value,
                "resumable_upload_url": file_resumable_upload_url,
                "file_blob_name": file_blob_name
            }
            user_files_row_data.append(file_data)
            
            user_files_response_data[file.file_request_id] = ResumableUploadResponseFileData(
                **file_data,
                file_id=file_data.get("id")
            )
            
        user_files_crud.create_user_files_rows(files_row_data=user_files_row_data, db_session=db_session, auto_commit=False)
        
        db_session.commit()
        response.data = UserFilesResumableUploadResponse(files=user_files_response_data).model_dump(mode="json")
        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN GENERATING RESUMABLE UPLOAD LINKS FOR USER FILES :: {e}")
    
    return response


async def file_upload_success_controller(data: FileUploadSuccessRequest, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        user_file_row = user_files_crud.get_user_files_row(file_id=data.file_id, folder_id=data.folder_id, user_id=user_authentication.user_id, db_session=db_session, columns=['*'])
        file_row_update_data = {
            "file_upload_status": UserFilesUploadStatus.OK.value
        }
        
        user_files_crud.update_user_files_row(update_data=file_row_update_data, folder_id=data.folder_id, file_id=data.file_id, user_id=user_authentication.user_id, db_session=db_session, auto_commit=False)
        folder_content_row_data = {
            "user_id": user_authentication.user_id,
            "folder_id": data.folder_id,
            "id": user_file_row.id,
            "file_name": user_file_row.file_name,
            "file_size": user_file_row.file_size,
            "file_upload_status": UserFilesUploadStatus.OK.value,
            "file_last_modified": user_file_row.file_last_modified,
            "file_type": user_file_row.file_type,
            "file_thumbnail_url": user_file_row.file_thumbnail_url,
        }
        
        user_files_crud.create_folder_content_rows_for_files(files_row_data=[folder_content_row_data], db_session=db_session, auto_commit=False)
        db_session.commit()
        
        response.data = {
            "folder_content": UserFolderContentMetadata(
                content_type=FolderContentsContentType.FILE.value,
                content_id=folder_content_row_data.get('id'),
                content_name=folder_content_row_data.get('file_name'),
                content_size=folder_content_row_data.get('file_size'),
                content_last_modified=folder_content_row_data.get('file_last_modified'),
                content_file_type=folder_content_row_data.get('file_type'),
                content_thumbnail_url=folder_content_row_data.get('file_thumbnail_url'),
            )
        }
        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"FAILED TO CHANGE THE FILE STATUS TO SUCCESS :: {data} :: {e}")
    
    return response


async def get_folder_contents_controller(folder_id: str, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        folder_details = user_files_crud.get_folder_details(folder_id=folder_id, user_id=user_authentication.user_id, db_session=db_session)
        folder_contents_rows = user_files_crud.get_folder_contents_data(folder_id=folder_id, user_id=user_authentication.user_id, db_session=db_session)
        
        if folder_details:
            response.data = UserFolderContentsResponse(
                folder_name=folder_details.folder_name,
                folder_size=0,
                folder_last_modified=folder_details.folder_last_modified,
                folder_content_count=len(folder_contents_rows) if type(folder_contents_rows) is list else 0,
                folder_content=[])
            
            if folder_contents_rows:
                for content in folder_contents_rows:
                    response.data.folder_size += int(content.content_size)
                    response.data.folder_content.append(UserFolderContentMetadata(
                        content_type=content.content_type,
                        content_id=content.content_id,
                        content_name=content.content_name,
                        content_size=content.content_size,
                        content_last_modified=content.content_last_modified,
                        content_file_type=content.content_file_type,
                        content_thumbnail_url=content.content_thumbnail_url,
                    ))
        
        else:
            response.status = 'error'
            response.status_code = 404
            response.data = APIErrorMessage(message='Folder does not exist')
        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN GETTING USER FOLDER CONTENTS :: {e}")
    
    return response


async def delete_folder_content_controller(content_id: str, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        delete_response = user_files_crud.delete_folder_content_row(content_id=content_id, user_id=user_authentication.user_id, db_session=db_session)
        user_files_crud.delete_user_files_row(file_id=content_id, user_id=user_authentication.user_id, db_session=db_session)
        
        if delete_response:
            db_session.commit()
            
            response.data = {
                "message": "Content deleted successfully"
            }
        
        else:
            response.status = API_STATUS_STRINGS.ERROR.value
            response.status_code = 404
            response.data = {
                "message": "Content not found"
            }
        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN DELETING FOLDER CONTENT :: {e}")
    
    return response

async def get_file_data_controller(file_id: str, folder_id: str, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        file_row = user_files_crud.get_user_files_row(file_id=file_id, folder_id=folder_id, user_id=user_authentication.user_id, db_session=db_session, columns=[
            UserFiles.file_blob_name
        ])
        
        if file_row:
            file_blob_name = file_row.file_blob_name
            file_bytes_data = await download_gcs_file_as_bytes(bucket_name=settings.gcs_bucket_name, blob_name=file_blob_name)
            
            response.data = {
                "file_bytes_data": io.BytesIO(file_bytes_data),
                "file_blob_name": file_blob_name
            }

        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN GETTING FILE BINARY DATA :: {e}")
    
    return response

async def get_file_details_controller(file_id: str, folder_id: str, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        file_row = user_files_crud.get_user_files_row(file_id=file_id, folder_id=folder_id, user_id=user_authentication.user_id, db_session=db_session, columns=[
            UserFiles.id, UserFiles.file_name, UserFiles.file_type, UserFiles.file_size,
            UserFiles.file_public_url, UserFiles.file_thumbnail_url, UserFiles.file_last_modified
        ])
        
        if file_row:
            file_row_dict = file_row._asdict()
            response.data = {
                "file_details": UserFileDetails(**file_row_dict, file_id=file_row_dict.get('id'))
            }
        

        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN GETTING USER FILE DETAILS :: {e}")
    
    return response


async def update_file_controller(file_id: str, file_modified_at: int, folder_id: str, user_file: UploadFile, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        user_id = user_authentication.user_id
        
        file_type = get_file_type_from_mime_type(mime_type=user_file.content_type)
        file_name_without_spaces = user_file.filename.replace(' ', '_')
        file_blob_name = f'{user_id}/{file_id}_{file_name_without_spaces}'
        file_public_url = await upload_file_to_gcs(bucket_name=settings.gcs_bucket_name, blob_to_upload=user_file, blob_file_path=file_blob_name)
        file_thumbnail_url = await get_file_thumbnail_url(file_type=file_type, file=user_file)
        
        user_file_row_update_data = {
            "file_name": user_file.filename,
            "file_type": file_type,
            "file_size": user_file.size,
            "file_public_url": file_public_url,
            "file_thumbnail_url": file_thumbnail_url,
            "file_last_modified": datetime.datetime.fromtimestamp(file_modified_at / 1000),
            "file_upload_status": UserFilesUploadStatus.OK.value,
            "file_blob_name": file_blob_name
        }
        
        folder_content_row_update_data = {
            "content_name": user_file.filename,
            "content_file_type": file_type,
            "content_size": user_file.size,
            "content_thumbnail_url": file_thumbnail_url,
            "content_last_modified": datetime.datetime.fromtimestamp(file_modified_at / 1000),
            "content_upload_status": UserFilesUploadStatus.OK.value,
        }
        
        user_files_crud.update_user_files_row(update_data=user_file_row_update_data, folder_id=folder_id,
                                              file_id=file_id, user_id=user_id, db_session=db_session, auto_commit=False)
        
        user_files_crud.update_folder_content_row(update_data=folder_content_row_update_data, content_id=file_id, user_folder_id=folder_id, user_id=user_id, db_session=db_session, auto_commit=False)
        db_session.commit()
        
        response.data = {
            "file": UserFileDetails(**user_file_row_update_data, file_id=file_id)
        }
        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN UPDATING USER USER FILE :: {e}")
    
    return response

async def delete_file_controller(file_id: str, user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        user_files_crud.delete_folder_content_row(content_id=file_id, user_id=user_authentication.user_id, db_session=db_session)
        user_files_crud.delete_user_files_row(file_id=file_id, user_id=user_authentication.user_id, db_session=db_session)
        
        db_session.commit()
        
        response.data = {
            "message": "File deleted successfully"
        }
        
    except Exception as e:
        db_session.rollback()
        response.status = API_STATUS_STRINGS.ERROR.value
        response.status_code = 500
        
        logger.exception(f"ERROR IN DELETING FILE :: {e}")
    
    return response