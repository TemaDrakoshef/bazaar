from src.domain.entities.media import MediaType
from src.domain.exceptions import MediaValidationError

IMAGE_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/bmp"})
VIDEO_CONTENT_TYPES = frozenset({"video/mp4", "video/quicktime"})

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024

_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/bmp": "bmp",
    "video/mp4": "mp4",
    "video/quicktime": "mov",
}


def validate_media_type(media_type: MediaType) -> None:
    if media_type not in (MediaType.IMAGE, MediaType.VIDEO):
        raise MediaValidationError("unsupported media type")


def validate_content_type(media_type: MediaType, content_type: str) -> str:
    """Validate the MIME type and return the file extension for the storage key."""
    allowlist = (
        IMAGE_CONTENT_TYPES if media_type == MediaType.IMAGE else VIDEO_CONTENT_TYPES
    )
    if content_type not in allowlist:
        raise MediaValidationError(
            f"content type {content_type!r} is not allowed for "
            f"{media_type.value.lower()}"
        )
    return _EXTENSIONS[content_type]


def validate_file_size(media_type: MediaType, file_size: int) -> None:
    if file_size <= 0:
        raise MediaValidationError("file_size must be positive")
    max_size = (
        MAX_IMAGE_SIZE_BYTES if media_type == MediaType.IMAGE else MAX_VIDEO_SIZE_BYTES
    )
    if file_size > max_size:
        raise MediaValidationError(
            f"{media_type.value.lower()} exceeds the maximum size of {max_size} bytes"
        )
