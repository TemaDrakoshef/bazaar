import aioboto3

from src.infrastructure.config.settings import Settings


class S3StorageService:
    """MinIO object storage operations used by the catalog context."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _client_kwargs(self, *, public: bool) -> dict[str, object]:
        endpoint = (
            self._settings.S3_PUBLIC_URL if public else self._settings.S3_ENDPOINT_URL
        )
        return {
            "endpoint_url": endpoint,
            "aws_access_key_id": self._settings.S3_ACCESS_KEY,
            "aws_secret_access_key": self._settings.S3_SECRET_KEY,
            "region_name": "us-east-1",
        }

    @property
    def bucket(self) -> str:
        return self._settings.S3_BUCKET_NAME  # type: ignore[no-any-return]

    async def generate_presigned_upload_url(
        self, key: str, content_type: str, expires_in: int = 600
    ) -> str:
        """Return a presigned PUT URL valid for ``expires_in`` seconds."""
        session = aioboto3.Session()
        async with session.client("s3", **self._client_kwargs(public=True)) as s3:
            return await s3.generate_presigned_url(  # type: ignore[no-any-return]
                "put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )

    async def delete_object(self, key: str) -> None:
        """Delete an object from the bucket."""
        session = aioboto3.Session()
        async with session.client("s3", **self._client_kwargs(public=False)) as s3:
            await s3.delete_object(Bucket=self.bucket, Key=key)

    def public_url(self, key: str) -> str:
        """Build the public (anonymous read) URL for an object key."""
        base = self._settings.S3_PUBLIC_URL.rstrip("/")
        return f"{base}/{self.bucket}/{key}"
