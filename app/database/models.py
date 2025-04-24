import uuid
import app.database.db_enums as db_enums

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.ext.declarative import declarative_base

from app.database.db_enums_classes import FolderContentsUploadStatus, UserFilesUploadStatus



class BaseModel:
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())

Base = declarative_base(cls=BaseModel)

class UserProfile(Base):
    __tablename__ = "user_profile"
    user_name = Column(String(64), nullable=False)
    user_email = Column(String(256), nullable=False)
    user_profile_image = Column(String, nullable=True)
    root_folder_id = Column(String(32))
    token = Column(String(32), nullable=False)
    

class UserFolders(Base):
    __tablename__ = "user_folders"
    user_id = Column(ForeignKey(UserProfile.id))
    folder_name = Column(String(64), nullable=False)
    folder_last_modified = Column(DateTime(timezone=True), default=func.current_timestamp(), nullable=False)
    folder_size = Column(Numeric, default=0, nullable=False)
    folder_content_count = Column(Numeric, default=0, nullable=False)
    

class UserFiles(Base):
    __tablename__ = "user_files"
    user_id = Column(ForeignKey(UserProfile.id))
    folder_id = Column(ForeignKey(UserFolders.id))
    file_name = Column(String(256), nullable=False)
    file_type = Column(db_enums.user_files_file_type, nullable=True)
    file_size = Column(Numeric, default=0, nullable=False)
    file_public_url = Column(String, nullable=True)
    file_thumbnail_url = Column(String)
    file_last_modified = Column(DateTime(timezone=True), default=func.current_timestamp(), nullable=False)
    file_upload_status = Column(db_enums.user_files_upload_status, default=UserFilesUploadStatus.OK.value)
    resumable_upload_url = Column(String)
    file_blob_name = Column(String, nullable=False)
    

class FolderContents(Base):
    __tablename__ = 'folder_contents'
    user_id = Column(ForeignKey(UserProfile.id), nullable=False)
    user_folder_id = Column(ForeignKey(UserFolders.id), nullable=False)
    content_type = Column(db_enums.folder_contents_content_type, nullable=False)
    content_id = Column(String(32), nullable=False, unique=True)
    content_name = Column(String(256), nullable=False)
    content_size = Column(Numeric, default=0)
    content_upload_status = Column(db_enums.folder_contents_upload_status, default=FolderContentsUploadStatus.OK.value)
    content_last_modified = Column(DateTime(timezone=True), default=func.current_timestamp(), nullable=False)
    content_file_type = Column(db_enums.folder_contents_file_type, nullable=True)
    content_thumbnail_url = Column(String)
    
    