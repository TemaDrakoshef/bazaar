import datetime

from jose import JWTError

from src.domain.exceptions import InvalidRefreshTokenError, SessionExpiredError
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.refresh.request import RefreshRequest
from src.usecase.refresh.response import RefreshResponse


class RefreshUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def execute(self, request: RefreshRequest) -> RefreshResponse:
        try:
            payload = self.decode_token(request.refresh_token, expected_type="refresh")
        except JWTError as _ex:
            raise InvalidRefreshTokenError() from _ex

        session_id = payload.get("session_id")
        if not session_id:
            raise InvalidRefreshTokenError()

        async with self._uow as uow:
            session = await uow.session.get_by_id(session_id)
            if not session or not session.is_active:
                raise SessionExpiredError()

            presented_hash = self.hash_token(request.refresh_token)
            if session.refresh_token_hash is None or (
                presented_hash != session.refresh_token_hash
            ):
                raise InvalidRefreshTokenError()

            new_refresh_token = self.create_refresh_token(session.id)

            await uow.session.update(
                session.id,
                refresh_token_hash=self.hash_token(new_refresh_token),
                last_active_at=datetime.datetime.now(),
            )

            access_token = self.create_access_token(session.user_id, session.id)

            await uow.commit()

        return RefreshResponse(
            access_token=access_token, refresh_token=new_refresh_token
        )
