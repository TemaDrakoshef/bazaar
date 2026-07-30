from jose import JWTError

from src.usecase.base import AuthBaseUsecase
from src.usecase.validate.request import ValidateTokenRequest
from src.usecase.validate.response import ValidateTokenResponse


class ValidateTokenUsecase(AuthBaseUsecase):
    async def execute(self, request: ValidateTokenRequest) -> ValidateTokenResponse:
        try:
            payload = self.decode_token(request.access_token)
        except JWTError:
            return ValidateTokenResponse(valid=False, error_message="Invalid token")

        user_id = payload.get("user_id")
        if not user_id:
            return ValidateTokenResponse(valid=False, error_message="Invalid token")

        return ValidateTokenResponse(valid=True, user_id=user_id)
