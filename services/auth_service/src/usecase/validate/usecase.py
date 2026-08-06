from jose import JWTError

from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.response import ValidateTokenResponse


class ValidateTokenUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork | None = None):
        self._uow = uow

    async def execute(self, request: ValidateTokenRequest) -> ValidateTokenResponse:
        try:
            payload = self.decode_token(request.access_token, expected_type="access")
        except JWTError:
            return ValidateTokenResponse(valid=False, error_message="Invalid token")

        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        if not user_id or not session_id:
            return ValidateTokenResponse(valid=False, error_message="Invalid token")

        if self._uow is not None:
            async with self._uow as uow:
                session = await uow.session.get_by_id(session_id)
                if not session or not session.is_active:
                    return ValidateTokenResponse(
                        valid=False, error_message="Session is no longer active"
                    )

        return ValidateTokenResponse(valid=True, user_id=user_id)
