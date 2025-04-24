from typing import List
import uuid
from sqlalchemy.orm.session import Session

from app.crud.generic_crud import GenericCrud
from app.database.models import UserFolders, UserProfile
from app.schemas.user_schemas import UserLogin

def get_user_profile_user_id(user_id: str, db_session: Session):
    existing_user_id = None
    
    user_rows = GenericCrud.get_rows(table_model=UserProfile, query_conditions=[UserProfile.id == user_id], columns=[UserProfile.id], limit=1, db_session=db_session)
    if user_rows:
        existing_user_id = user_rows[0].id
        
    return existing_user_id


def create_user_profile_row(data: UserLogin, user_token: str, db_session: Session, auto_commit: bool):
    user_row_data = UserProfile(
        id = data.user_uid,
        user_name = data.user_name,
        user_email = data.user_email,
        user_profile_image = data.user_profile_image,
        token = user_token
    )
    
    GenericCrud.create_row(table_row_data=user_row_data, db_session=db_session, auto_commit=auto_commit)


def update_user_profile_row(user_id: str, update_data: dict, db_session: Session, auto_commit: bool):
    GenericCrud.update_row(table_model=UserProfile, query_condition=[UserProfile.id == user_id], update_data=update_data, db_session=db_session, auto_commit=auto_commit)
    
def create_root_folder_and_update_user_row(user_id: str, folder_name: str, db_session: Session, auto_commit: bool):
    folder_id = uuid.uuid4().hex
    
    user_folder_row = UserFolders(
        id = folder_id,
        user_id = user_id,
        folder_name = folder_name,
    )
    
    GenericCrud.create_row(table_row_data=user_folder_row, db_session=db_session, auto_commit=False)
    
    user_profile_update_data = {
        "root_folder_id": folder_id
    }
    
    update_user_profile_row(user_id=user_id, update_data=user_profile_update_data, db_session=db_session, auto_commit=False)
    
    db_session.commit()
    
def get_user_profile_user_crud(user_id: str, db_session: Session, columns: List = ['*']):
    user_row = None
    
    user_rows = GenericCrud.get_rows(table_model=UserProfile, query_conditions=[UserProfile.id == user_id], columns=columns, db_session=db_session, limit=1)
    
    if user_rows:
        user_row = user_rows[0]
        
    return user_row