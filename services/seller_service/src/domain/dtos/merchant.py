from pydantic import BaseModel, Field


class MerchantCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    inn: str = Field(pattern=r"^\d{10}$|^\d{12}$")
    user_id: str = Field(min_length=1)


class VerifyAccessDTO(BaseModel):
    user_id: str
    merchant_id: int


class VerifyAccessResult(BaseModel):
    allowed: bool
    role: str = ""
