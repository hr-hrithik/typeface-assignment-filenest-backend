import uuid
import logging

import app.crud.user_crud as user_crud

from sqlalchemy.orm.session import Session

from app.constants.common_constants import API_STATUS_STRINGS
from app.database.models import UserProfile
from app.schemas.authentication_schemas import UserAuthentication
from app.schemas.common_schemas import APIErrorMessage, APIResponse
from app.schemas.user_schemas import UserLogin, UserProfileResponse

logger = logging.getLogger(__name__)

def login_controller(data: UserLogin, db_session: Session):
    response = APIResponse()
    try:
        existing_user_id = user_crud.get_user_profile_user_id(user_id=data.user_uid, db_session=db_session)
        user_token = uuid.uuid4().hex
        
        if existing_user_id:
            user_profile_id = existing_user_id
            
            logger.info(f"User already exists, upserting data :: user_profile id = {user_profile_id}")
            update_data = {
                "id": data.user_uid,
                "user_email": data.user_email,
                "user_name": data.user_name,
                "user_profile_image": data.user_profile_image,
                "token": user_token
            }
            
            user_crud.update_user_profile_row(user_id=data.user_uid, update_data=update_data, db_session=db_session, auto_commit=True)
        
        else:
            user_crud.create_user_profile_row(data=data, user_token=user_token, db_session=db_session, auto_commit=True)
            user_crud.create_root_folder_and_update_user_row(user_id=data.user_uid, folder_name=f"{data.user_name}'s Nest", db_session=db_session, auto_commit=True)
            
        response.data = {
            "user_token": user_token
        }
    
    except Exception as e:
        response.status_code = 500
        response.status = API_STATUS_STRINGS.ERROR.value
        response.data = APIErrorMessage(message="Failed to login")
        
        logger.exception(f"ERROR IN USER LOGIN :: {e}")
    
    return response

def get_user_profile_controller(user_authentication: UserAuthentication, db_session: Session):
    response = APIResponse()
    try:
        user_row = user_crud.get_user_profile_user_crud(user_id=user_authentication.user_id, db_session=db_session, columns=[
            UserProfile.id,
            UserProfile.user_name,
            UserProfile.user_email,
            UserProfile.user_profile_image,
            UserProfile.root_folder_id])
        
        if user_row:
            response.data = {
                "user_profile": UserProfileResponse(**user_row._asdict(), user_uid=user_row.id)
            }
        # fu
    
    except Exception as e:
        response.status_code = 500
        response.status = API_STATUS_STRINGS.ERROR.value
        response.data = APIErrorMessage(message='An error occured while getting user profile')
        
        logger.exception(f"ERROR IN GETTING USER PROFILE :: {e}")
    
    return response