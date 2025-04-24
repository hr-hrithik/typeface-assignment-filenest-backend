from pydantic import BaseModel

class UserAuthentication(BaseModel):
    user_id: str
    
class AuthenticationResponse(BaseModel):
    status: str = 'ok'
    status_code: int = 200
    description: str = 'Success'
    data: UserAuthentication = None