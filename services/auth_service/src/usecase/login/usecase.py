import datetime

from src.domain.exceptions import InvalidCredentialsError
from src.domain.validation import validate_email, validate_password
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.login.request import LoginRequest
from src.usecase.login.response import LoginResponse


class LoginUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def execute(self, request: LoginRequest) -> LoginResponse:
        validate_email(request.email)
        validate_password(request.password)

        async with self._uow as uow:
            user = await uow.account.get_one_or_none(email=request.email)
            if not user or not user.is_active:
                raise InvalidCredentialsError()

            if not self.verify_password(request.password, user.password_hash):
                raise InvalidCredentialsError()

            session = await uow.session.get_one_or_none(user_id=user.id)
            if not session:
                raise InvalidCredentialsError()

            refresh_token = self.create_refresh_token(session.id)

            await uow.session.update(
                session.id,
                is_active=True,
                refresh_token_hash=self.hash_token(refresh_token),
                last_active_at=datetime.datetime.now(),
            )

            access_token = self.create_access_token(user.id, session.id)

            await uow.commit()

        return LoginResponse(access_token=access_token, refresh_token=refresh_token)
