from enum import Enum

class UserFilesFileType(Enum):
    ARCHIVE = 'Archive'
    AUDIO = 'Audio'
    CODE = 'Code'
    DOCUMENT = 'Document'
    IMAGE = 'Image'
    VIDEO = 'Video'
    OTHERS = 'Others'
    
class FolderContentsContentType(Enum):
    FILE = 'file'
    FOLDER = 'folder'
    
class FolderContentsContentType(Enum):
    FILE = 'file'
    FOLDER = 'folder'
    
class UserFilesUploadStatus(Enum):
    OK = 'ok'
    PENDING = 'pending'
    ERROR = 'error'
    
class FolderContentsUploadStatus(Enum):
    OK = 'ok'
    PENDING = 'pending'
    ERROR = 'error'