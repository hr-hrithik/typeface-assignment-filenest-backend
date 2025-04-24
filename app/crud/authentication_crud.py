from sqlalchemy.orm.session import Session

from app.crud.generic_crud import GenericCrud
from app.database.models import UserProfile

def get_user_id_from_token(user_token: str, db_session: Session):
    user_id = None
    
    user_rows = GenericCrud.get_rows(table_model=UserProfile, query_conditions=[UserProfile.token == user_token], columns=[UserProfile.id], limit=1, db_session=db_session)
    if user_rows:
        user_id = user_rows[0].id
        
    return user_id