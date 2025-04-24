from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_connection_url: str = 'postgresql://local_admin:local_password@localhost/typeface_assignment'
    service_url: str = 'http://localhost:8000'
    
    gcs_bucket_name: str = 'typeface-assignment'
    
@lru_cache
def get_settings():
    return Settings()