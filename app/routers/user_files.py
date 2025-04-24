from fastapi import APIRouter, Depends, Form, Header, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm.session import Session

from app.controllers.user_files_controller import delete_file_controller, delete_folder_content_controller, file_upload_success_controller, get_file_data_controller, get_file_details_controller, get_folder_contents_controller, get_user_files_controller, update_file_controller, upload_user_files_controller, user_files_resumable_upload_controller
from app.database.db_connection import get_db
from app.helpers.authentication_helpers import authenticate_user
from app.schemas.user_files_schemas import FileUploadSuccessRequest, UserFilesResumableUploadRequest

router = APIRouter()


@router.get(path='/get-user-files')
async def get_user_files(page: int = 1, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await get_user_files_controller(user_id=user_authentication.user_id, page=page, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.post(path='/upload-user-file')
async def upload_user_files(file_modified_at: int = Form(), folder_id: str = Form(), user_file: UploadFile = Form(), authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await upload_user_files_controller(file_modified_at=file_modified_at, user_id=user_authentication.user_id, folder_id=folder_id, user_file=user_file, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.post(path='/user-files-resumable-upload')
async def user_files_resumable_upload(data: UserFilesResumableUploadRequest, origin = Header(default=None), authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await user_files_resumable_upload_controller(data=data, user_authentication=user_authentication, origin=origin, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.post(path='/file-upload-success')
async def file_upload_success(data: FileUploadSuccessRequest, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await file_upload_success_controller(data=data, user_authentication=user_authentication, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.get(path='/get-folder-contents')
async def get_folder_contents(folder_id: str, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await get_folder_contents_controller(folder_id=folder_id, user_authentication=user_authentication, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.delete(path='/delete-folder-content/{content_id}')
async def delete_folder_content(content_id: str, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await delete_folder_content_controller(content_id=content_id, user_authentication=user_authentication, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.get(path='/get-file-data')
async def get_file_data(file_id: str, folder_id: str, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await get_file_data_controller(file_id=file_id, folder_id=folder_id, user_authentication=user_authentication, db_session=db_session)
    return StreamingResponse(content=response.data.get('file_bytes_data'), status_code=response.status_code)

@router.get(path='/get-file-details')
async def get_file_details(file_id: str, folder_id: str, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await get_file_details_controller(file_id=file_id, folder_id=folder_id, user_authentication=user_authentication, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.put(path='/update-file')
async def update_file(file_id: str = Form(), file_modified_at: int = Form(), folder_id: str = Form(), user_file: UploadFile = Form(), authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await update_file_controller(file_id=file_id, file_modified_at=file_modified_at, user_file=user_file, folder_id=folder_id, user_authentication=user_authentication, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.delete(path='/delete-file/{file_id}')
async def delete_file(file_id: str, authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    
    response = await delete_file_controller(file_id=file_id, user_authentication=user_authentication, db_session=db_session)
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)
