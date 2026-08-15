import datetime
import uuid

import structlog
from sqlalchemy.exc import IntegrityError

from src.domain.exceptions import UserAlreadyExistsError
from src.domain.validation import validate_signup_input
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.signup.request import SignUpRequest
from src.usecase.signup.response import SignUpResponse

logger = structlog.get_logger()


class SignUpUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def execute(self, request: SignUpRequest) -> SignUpResponse:
        validate_signup_input(request.email, request.phone, request.password)

        async with self._uow as uow:
            existing_user = await uow.account.get_one_or_none(email=request.email)
            if existing_user:
                raise UserAlreadyExistsError()

            hashed_password = self.hash_password(request.password)

            session_id = uuid.uuid4()
            refresh_token = self.create_refresh_token(session_id)

            try:
                account = await uow.account.create(
                    id=uuid.uuid4(),
                    email=request.email,
                    phone=request.phone,
                    password_hash=hashed_password,
                )

                await uow.session.create(
                    id=session_id,
                    user_id=account.id,
                    refresh_token_hash=self.hash_token(refresh_token),
                    last_active_at=datetime.datetime.now(),
                )
            except IntegrityError as exc:
                raise UserAlreadyExistsError() from exc

            access_token = self.create_access_token(account.id, session_id)

            await uow.commit()

        logger.info(
            "auth.signup.completed",
            account_id=str(account.id),
            email=request.email,
        )
        return SignUpResponse(access_token=access_token, refresh_token=refresh_token)
