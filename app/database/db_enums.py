from sqlalchemy.dialects.postgresql import ENUM

from app.database.db_enums_classes import FolderContentsContentType, FolderContentsUploadStatus, UserFilesFileType, UserFilesUploadStatus
from app.helpers.common import get_enum_values

user_files_file_type = ENUM(*get_enum_values(enum_class=UserFilesFileType), name='user_files_file_type', create_type=True)
folder_contents_content_type = ENUM(*get_enum_values(enum_class=FolderContentsContentType), name='folder_contents_content_type', create_type=True)
folder_contents_file_type = ENUM(*get_enum_values(enum_class=UserFilesFileType), name='folder_contents_file_type', create_type=True)
user_files_upload_status = ENUM(*get_enum_values(enum_class=UserFilesUploadStatus), name='user_files_upload_status', create_type=True)
folder_contents_upload_status = ENUM(*get_enum_values(enum_class=FolderContentsUploadStatus), name='folder_contents_upload_status', create_type=True)