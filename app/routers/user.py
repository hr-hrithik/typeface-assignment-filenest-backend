from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.controllers.user_controller import get_user_profile_controller, login_controller
from app.database.db_connection import get_db
from app.helpers.authentication_helpers import authenticate_user
from app.schemas.user_schemas import UserLogin

router = APIRouter()

@router.post(path='/login')
def login(data: UserLogin, db_session = Depends(get_db)):
    response = login_controller(data=data, db_session=db_session)
    
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

@router.get(path='/get-user-profile')
def get_user(authenticate = Depends(authenticate_user)):
    user_authentication, db_session = authenticate
    response = get_user_profile_controller(user_authentication=user_authentication, db_session=db_session)
    
    return JSONResponse(content=response.model_dump(mode="json"), status_code=response.status_code)

