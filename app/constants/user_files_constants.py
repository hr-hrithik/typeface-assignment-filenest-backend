from app.database.db_enums_classes import UserFilesFileType


GET_USER_FILES_PAGE_SIZE = 12

MIME_TYPE_FILE_TYPE_MAPPING = {
  ##Documents
  "application/pdf": UserFilesFileType.DOCUMENT.value,
  "application/msword": UserFilesFileType.DOCUMENT.value,
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": UserFilesFileType.DOCUMENT.value,
  "application/vnd.ms-excel": UserFilesFileType.DOCUMENT.value,
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": UserFilesFileType.DOCUMENT.value,
  "text/plain": UserFilesFileType.DOCUMENT.value,

  ##Images
  "image/jpeg": UserFilesFileType.IMAGE.value,
  "image/avif": UserFilesFileType.IMAGE.value,
  "image/png": UserFilesFileType.IMAGE.value,
  "image/gif": UserFilesFileType.IMAGE.value,
  "image/svg+xml": UserFilesFileType.IMAGE.value,
  "image/webp": UserFilesFileType.IMAGE.value,

  ##Videos
  "video/mp4": UserFilesFileType.VIDEO.value,
  "video/x-msvideo": UserFilesFileType.VIDEO.value,
  "video/quicktime": UserFilesFileType.VIDEO.value,

  ##Audio
  "audio/mpeg": UserFilesFileType.AUDIO.value,
  "audio/wav": UserFilesFileType.AUDIO.value,
  "audio/ogg": UserFilesFileType.AUDIO.value,

  ##Archives
  "application/zip": UserFilesFileType.ARCHIVE.value,
  "application/x-rar-compressed": UserFilesFileType.ARCHIVE.value,
  "application/x-7z-compressed": UserFilesFileType.ARCHIVE.value,
  "application/x-tar": UserFilesFileType.ARCHIVE.value,

  ##Code
  "text/javascript": UserFilesFileType.CODE.value,
  "text/html": UserFilesFileType.CODE.value,
  "text/css": UserFilesFileType.CODE.value,
  "application/json": UserFilesFileType.CODE.value,
  "application/javascript": UserFilesFileType.CODE.value,
  "application/x-python-code": UserFilesFileType.CODE.value,
}

DEFAULT_THUMBNAILS = {
  UserFilesFileType.ARCHIVE.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/archive.png",
  UserFilesFileType.AUDIO.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/audio.png",
  UserFilesFileType.CODE.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/code.png",
  UserFilesFileType.DOCUMENT.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/document.png",
  UserFilesFileType.IMAGE.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/image.png",
  UserFilesFileType.VIDEO.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/video.png",
  UserFilesFileType.OTHERS.value: "https://storage.googleapis.com/typeface-assignment/thumbnails/unknown.png",
}
