from datetime import timedelta
from typing import Optional, Tuple
import uuid

from django.conf import settings
from google.cloud import storage

# Map common content types to file extensions
_CONTENT_TYPE_EXT = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'application/pdf': 'pdf',
}


def _ext_from_content_type(content_type: str) -> str:
    return _CONTENT_TYPE_EXT.get(content_type, 'bin')


def get_bucket() -> storage.Bucket:
    if not settings.GCS_BUCKET:
        raise RuntimeError('GCS_BUCKET is not configured')
    client = storage.Client()
    return client.bucket(settings.GCS_BUCKET)


def build_object_name(property_id: int, resident_id: int, kind: str, content_type: str) -> str:
    """Build a deterministic object name path for resident uploads.
    kind: 'resident_photo' | 'aadhar_file'
    """
    ext = _ext_from_content_type(content_type)
    suffix = uuid.uuid4().hex
    base = settings.GCS_UPLOAD_PREFIX or 'properties'
    return f"{base}/{property_id}/residents/{resident_id}/{kind}/{suffix}.{ext}"


def generate_signed_upload_url(
    object_name: str,
    content_type: str,
    expires_in_seconds: Optional[int] = None,
) -> Tuple[str, str]:
    """Generate a V4 signed URL for uploading with PUT.
    Returns (signed_url, storage_url).
    """
    bucket = get_bucket()
    blob = bucket.blob(object_name)
    expiry = expires_in_seconds or settings.GCS_SIGNED_URL_EXPIRY or 900

    signed_url = blob.generate_signed_url(
        version='v4',
        expiration=timedelta(seconds=expiry),
        method='PUT',
        content_type=content_type,
    )
    storage_url = f"https://storage.googleapis.com/{bucket.name}/{object_name}"
    return signed_url, storage_url
