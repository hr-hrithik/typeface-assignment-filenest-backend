from typing import List
from sqlalchemy.orm.session import Session

from app.crud.generic_crud import GenericCrud
from app.database.db_enums_classes import FolderContentsContentType
from app.database.models import FolderContents, UserFiles, UserFolders

def create_user_files_rows(files_row_data: List[dict], db_session: Session, auto_commit: bool):
    user_files_rows = []
    
    for file_data in files_row_data:
        user_files_rows.append(UserFiles(
            **file_data
        ))
    
    GenericCrud.create_multiple_rows(table_rows_data=user_files_rows, db_session=db_session, auto_commit=auto_commit)

def update_user_files_row(update_data: dict, folder_id: str, file_id: str, user_id: str, db_session: Session, auto_commit: bool):
    GenericCrud.update_row(table_model=UserFiles, query_condition=[
        UserFiles.folder_id == folder_id, UserFiles.id == file_id,
        UserFiles.user_id == user_id], db_session=db_session, auto_commit=auto_commit, update_data=update_data)
    
def get_user_files_row(file_id: str, folder_id: str, user_id: str, db_session: Session, columns: List = ['*']):
    user_files_row = None
    
    user_files_rows = GenericCrud.get_rows(table_model=UserFiles, query_conditions=[
        UserFiles.id == file_id, UserFiles.folder_id == folder_id, UserFiles.user_id == user_id,
    ], columns=columns, db_session=db_session)
    
    if user_files_rows:
        user_files_row = user_files_rows[0]
        
    return user_files_row

def create_folder_content_rows_for_files(files_row_data: List[dict], db_session: Session, auto_commit: bool):
    folder_content_rows = []
    
    for file_data in files_row_data:
        folder_content_rows.append(FolderContents(
            user_id = file_data.get('user_id'),
            user_folder_id = file_data.get('folder_id'),
            content_type = FolderContentsContentType.FILE.value,
            content_id = file_data.get('id'),
            content_name = file_data.get('file_name'),
            content_size = file_data.get('file_size'),
            content_upload_status = file_data.get('file_upload_status'),
            content_last_modified = file_data.get('file_last_modified'),
            content_file_type = file_data.get('file_type'),
            content_thumbnail_url = file_data.get('file_thumbnail_url'),
        ))
        
    
    GenericCrud.create_multiple_rows(table_rows_data=folder_content_rows, db_session=db_session, auto_commit=auto_commit)

def get_folder_details(folder_id: str, user_id: str, db_session):
    folder_details = None
    
    folder_rows = GenericCrud.get_rows(table_model=UserFolders, query_conditions=[UserFolders.id == folder_id, UserFolders.user_id == user_id],
                                       db_session=db_session, columns=[UserFolders.folder_content_count, UserFolders.folder_name, UserFolders.folder_size,
                                                                       UserFolders.folder_last_modified])
    
    if folder_rows:
        folder_details = folder_rows[0]
        
    return folder_details

def get_folder_contents_data(folder_id: str, user_id: str, db_session: Session):
    folder_contents_rows = []
    
    folder_contents_rows = GenericCrud.get_rows(table_model=FolderContents, query_conditions=[FolderContents.user_folder_id == folder_id, FolderContents.user_id == user_id], db_session=db_session,
                                                columns=[FolderContents.content_type, FolderContents.content_id, FolderContents.content_name,
                                                         FolderContents.content_size, FolderContents.content_last_modified, FolderContents.content_file_type, FolderContents.content_thumbnail_url],
                                                order_by=[FolderContents.created_at.desc()])
    
    return folder_contents_rows

def delete_folder_content_row(content_id: str, user_id: str, db_session: Session):
    delete_response = GenericCrud.delete_row(table_model=FolderContents, query_condition=[FolderContents.content_id ==content_id, FolderContents.user_id == user_id], db_session=db_session, auto_commit=False)
    return delete_response

def update_folder_content_row(update_data: dict, content_id: str, user_folder_id: str, user_id: str, db_session: Session, auto_commit: bool):
    GenericCrud.update_row(table_model=FolderContents, query_condition=[
        FolderContents.user_folder_id == user_folder_id, FolderContents.user_id == user_id, FolderContents.content_id == content_id], update_data=update_data, db_session=db_session, auto_commit=auto_commit)