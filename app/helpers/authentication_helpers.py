import logging

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm.session import Session

import app.crud.authentication_crud as authentication_crud
from app.database.db_connection import get_db
from app.schemas.authentication_schemas import AuthenticationResponse, UserAuthentication

logger = logging.getLogger(__name__)

def authenticate_user(authorization: str = Header(default=None), db_session: Session = Depends(get_db)):
    response = AuthenticationResponse()
    
    try:
        user_id = authentication_crud.get_user_id_from_token(user_token=authorization, db_session=db_session)
        if user_id:
            user_authentication = UserAuthentication(
                user_id=user_id
            )
            
            response.data = user_authentication
            
        else:
            response.status = 'error'
            response.status_code = 401
            response.description = "Unauthorised request"
            response.data = None
        
    except Exception as e:
        logger.exception(f"ERROR IN AUTHENTICATING USER :: {e}")
        response.status = 'error'
        response.status_code = 500
        response.description = "Error in authenticating request"
        response.data = None
        
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.description)
    
    return response.data, db_session
        