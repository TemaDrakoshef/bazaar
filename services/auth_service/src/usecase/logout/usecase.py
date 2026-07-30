import datetime

from src.domain.exceptions import SessionNotFoundError
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.logout.request import LogoutRequest
from src.usecase.logout.response import LogoutResponse


class LogoutUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def execute(self, request: LogoutRequest) -> LogoutResponse:
        async with self._uow as uow:
            session = await uow.session.get_by_id(request.session_id)
            if not session:
                raise SessionNotFoundError()

            await uow.session.update(
                session.id,
                is_active=False,
                last_active_at=datetime.datetime.now(),
            )

            await uow.commit()

        return LogoutResponse()
