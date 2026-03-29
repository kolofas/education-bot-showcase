from datetime import datetime
from pydantic import BaseModel, Field


class AppBaseModel(BaseModel):
    model_config = {
        "from_attributes": True
    }


class UserCheckResponse(AppBaseModel):
    exists: bool


class UserRegistrationRequest(AppBaseModel):
    """Pydantic модель для данных регистрации пользователя"""
    username: str = Field(..., min_length=3, max_length=64)
    user_id: int
    password: str


class AuthorizedResponse(AppBaseModel):
    authorized: bool


class MessageResponse(AppBaseModel):
    message: str


class TokenResetResponse(AppBaseModel):
    access_token: str


class UserLoginRequest(AppBaseModel):
    user_id: int
    password: str


class UserLoginResponse(AppBaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(AppBaseModel):
    access_token: str


class UserProfileResponse(AppBaseModel):
    user_id: int
    username: str = Field(alias="login")


class UpdateProfileRequest(AppBaseModel):
    username: str


class MaterialBase(AppBaseModel):
    title: str
    description: str
    file_url: str


class MaterialCreateRequest(MaterialBase):
    user_id: int
    token: str


class MaterialOut(MaterialBase):
    id: int


class MaterialData(MaterialCreateRequest):
    id: int


class SchoolServiceData(AppBaseModel):
    title: str
    description: str
    price: float
    user_id: int


class SchoolServiceOut(AppBaseModel):
    id: int
    title: str
    description: str
    price: float


class SchoolServiceCreateRequest(AppBaseModel):
    title: str
    description: str
    price: float
    user_id: int
    token: str


class BonusCreateRequest(AppBaseModel):
    title: str
    description: str
    action_text: str
    user_id: int
    token: str
    is_active: bool = True


class BonusOut(AppBaseModel):
    id: int
    title: str
    description: str
    action_text: str
    is_active: bool
    created_at: datetime


class SocialNetworkCreateRequest(AppBaseModel):
    user_id: int
    platform: str
    url: str | None = None
    phone: str | None = None
    token: str | None = None


class SocialNetworkOut(AppBaseModel):
    id: int
    platform: str
    url: str | None = None
    phone: str | None = None
