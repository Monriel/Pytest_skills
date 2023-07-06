from pydantic import BaseModel
from pydantic.utils import to_lower_camel


class AppSmartProfileDto(BaseModel):
    """Базовый класс DTO сервиса app-smart-profile"""
    class Config:
        alias_generator = to_lower_camel

    def dict(self, *args, **kwargs):
        return super().dict(exclude_unset=True, by_alias=True, *args, **kwargs)
