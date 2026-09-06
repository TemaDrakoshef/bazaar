from abc import ABC, abstractmethod


class AbstractStorageService(ABC):
    """Port for the object storage used by product media."""

    @property
    @abstractmethod
    def bucket(self) -> str: ...

    @abstractmethod
    async def generate_presigned_upload_url(
        self, key: str, content_type: str, expires_in: int = 600
    ) -> str: ...

    @abstractmethod
    async def delete_object(self, key: str) -> None: ...

    @abstractmethod
    def public_url(self, key: str) -> str: ...
