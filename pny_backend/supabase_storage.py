"""
Custom Django storage backend using Supabase Storage (no AWS/S3).
Uses the official supabase-py client.
"""
import os
from io import BytesIO
from urllib.parse import urljoin

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from supabase import create_client, Client
from decouple import config as env_config


@deconstructible
class SupabaseStorage(Storage):
    """
    Django storage backend that stores files in Supabase Storage.
    Requires env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_STORAGE_BUCKET
    """

    def __init__(self, bucket_name=None):
        self.bucket_name = bucket_name or env_config('SUPABASE_STORAGE_BUCKET', default='resumes')
        self._client: Client = create_client(
            env_config('SUPABASE_URL'),
            env_config('SUPABASE_SERVICE_KEY'),  # service role key — never expose to frontend
        )

    @property
    def bucket(self):
        return self._client.storage.from_(self.bucket_name)

    def _save(self, name, content):
        """Upload file to Supabase Storage."""
        content.seek(0)
        file_data = content.read()
        # Supabase expects bytes; content-type is inferred from filename
        self.bucket.upload(
            path=name,
            file=file_data,
            file_options={"upsert": "true"},
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
            files = self.bucket.list(os.path.dirname(name))
            file_names = [f['name'] for f in files]
            return os.path.basename(name) in file_names
        except Exception:
            return False

    def url(self, name):
        """Return a signed URL valid for 1 hour."""
        try:
            result = self.bucket.create_signed_url(name, expires_in=3600)
            return result.get('signedURL', '')
        except Exception:
            return ''

    def size(self, name):
        """Return file size in bytes."""
        try:
            files = self.bucket.list(os.path.dirname(name))
            for f in files:
                if f['name'] == os.path.basename(name):
                    return f.get('metadata', {}).get('size', 0)
        except Exception:
            pass
        return 0
