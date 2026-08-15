import structlog
from jose import JWTError

from src.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.response import ValidateTokenResponse

logger = structlog.get_logger()


class ValidateTokenUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork | None = None):
        self._uow = uow

    async def execute(self, request: ValidateTokenRequest) -> ValidateTokenResponse:
        try:
            payload = self.decode_token(request.access_token, expected_type="access")
        except JWTError:
            logger.warning("auth.token.rejected", reason="invalid_or_expired_token")
            return ValidateTokenResponse(valid=False, error_message="Invalid token")

        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        if not user_id or not session_id:
            logger.warning("auth.token.rejected", reason="missing_claims")
            return ValidateTokenResponse(valid=False, error_message="Invalid token")

        if self._uow is not None:
            async with self._uow as uow:
                session = await uow.session.get_by_id(session_id)
                if not session or not session.is_active:
                    logger.warning(
                        "auth.token.rejected",
                        reason="session_inactive_or_not_found",
                        session_id=str(session_id),
                    )
                    return ValidateTokenResponse(
                        valid=False, error_message="Session is no longer active"
                    )

        logger.debug("auth.token.validated", valid=True, user_id=str(user_id))
        return ValidateTokenResponse(valid=True, user_id=user_id)
