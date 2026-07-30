import datetime
import uuid

from src.domain.exceptions import UserAlreadyExistsError
from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.signup.request import SignUpRequest
from src.usecase.signup.response import SignUpResponse


class SignUpUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def execute(self, request: SignUpRequest) -> SignUpResponse:
        async with self._uow as uow:
            existing_user = await uow.account.get_one_or_none(email=request.email)
            if existing_user:
                raise UserAlreadyExistsError()

            hashed_password = self.hash_password(request.password)

            account = await uow.account.create(
                id=uuid.uuid4(),
                email=request.email,
                phone=request.phone,
                password_hash=hashed_password,
            )

            session = await uow.session.create(
                id=uuid.uuid4(),
                user_id=account.id,
                last_active_at=datetime.datetime.now(),
            )

            access_token = self.create_access_token(account.id)
            refresh_token = self.create_refresh_token(session.id)

            await uow.commit()

        return SignUpResponse(access_token=access_token, refresh_token=refresh_token)
