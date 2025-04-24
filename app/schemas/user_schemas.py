from typing import Optional
from pydantic import BaseModel

class UserLogin(BaseModel):
    user_name: str
    user_email: str
    user_uid: str
    user_profile_image: Optional[str] = None
    
class UserProfileResponse(BaseModel):
    user_uid: str
    user_name: str
    user_email: str
    user_profile_image: Optional[str] = None
    root_folder_id: str
    