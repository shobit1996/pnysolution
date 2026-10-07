"""
Custom Django storage backend using Supabase Storage (no AWS/S3).
Uses the official supabase-py client v2.
"""
import os
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from decouple import config as env_config


@deconstructible
class SupabaseStorage(Storage):
    """
    Django storage backend that stores files in Supabase Storage.
    Requires env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_STORAGE_BUCKET
    """

    def __init__(self, bucket_name=None):
        self.bucket_name = bucket_name or env_config('SUPABASE_STORAGE_BUCKET', default='resumes')
        self._supabase_url = env_config('SUPABASE_URL')
        self._supabase_key = env_config('SUPABASE_SERVICE_KEY')
        self._client = None  # lazy init — avoid cold-start crash

    def _get_client(self):
        """Lazy-initialize the Supabase client on first use."""
        if self._client is None:
            from supabase import create_client
            self._client = create_client(self._supabase_url, self._supabase_key)
        return self._client

    @property
    def bucket(self):
        return self._get_client().storage.from_(self.bucket_name)

    def _save(self, name, content):
        """Upload file to Supabase Storage."""
        content.seek(0)
        file_data = content.read()
        # Determine content type from file extension
        import mimetypes
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'

        self.bucket.upload(
            path=name,
            file=file_data,
            file_options={
                "content-type": content_type,
                "upsert": True,  # boolean, not string
            },
        )
        return name

    def _open(self, name, mode='rb'):
        """Download file from Supabase Storage."""
        data = self.bucket.download(name)
        return ContentFile(data)

    def delete(self, name):
        """Delete file from Supabase Storage."""
        try:
            self.bucket.remove([name])
        except Exception:
            pass

    def exists(self, name):
        """Check if a file exists in Supabase Storage."""
        try:
            dir_path = os.path.dirname(name)
            files = self.bucket.list(dir_path if dir_path else '')
            file_names = [f['name'] for f in files if isinstance(f, dict)]
            return os.path.basename(name) in file_names
        except Exception:
            return False

    def url(self, name):
        """Return a signed URL valid for 1 hour."""
        try:
            result = self.bucket.create_signed_url(name, expires_in=3600)
            # supabase-py v2 returns dict with 'signedURL' key
            if isinstance(result, dict):
                return result.get('signedURL', result.get('signed_url', ''))
            return ''
        except Exception:
            return ''

    def size(self, name):
        """Return file size in bytes."""
        try:
            dir_path = os.path.dirname(name)
            files = self.bucket.list(dir_path if dir_path else '')
            for f in files:
                if isinstance(f, dict) and f.get('name') == os.path.basename(name):
                    return f.get('metadata', {}).get('size', 0)
        except Exception:
            pass
        return 0
