"""Модели описания проф. тегов в разделе общие сведения сервиса Smart-Profile"""
from typing import Optional
from enum import Enum
from pydantic import Field
from datetime import date
from uuid import UUID

from dto.app_smart_profile.schema.generic import AppSmartProfileDto


class Position(Enum):
    """Расположение опыта"""
    LEFT = 'LEFT'


class Responsibility(AppSmartProfileDto):
    """Схема ответа обязанностей """
    workExpCustomInfoId: UUID = Field(description='Uuid уже сохраненных обязанностей', alias='workExpCustomInfoId')
    text: str = Field(description='Текст обязанностей')


class ProfessionalArea(AppSmartProfileDto):
    """Схема профессиональной области """
    id: int = Field(description='Id профессиональной области')
    name: str = Field(description='Название профессиональной области')


class EmployeeInAchievements(AppSmartProfileDto):
    """Схема ответа списка участников в достижении """
    userId: UUID = Field(description='Uuid сотрудника', alias='userId')
    photoUrl: str = Field(description='url фотографии аватарки', alias='photoUrl')
    firstName: str = Field(description='Имя', alias='firstName')
    lastName: str = Field(description='Фамилия', alias='lastName')
    secondName: str = Field(description='Отчество', alias='secondName')
    position: str = Field(description='Должность')
    fired: bool = Field(description='Признак уволенного сотрудника')


class Company(AppSmartProfileDto):
    """Схема ответа добавление опыта внесенного вручную """
    unconfirmedExpId: int = Field(description='Id неподтвержденного опыта работы', alias='unconfirmedExpId')
    professionalAreaId: int = Field(description='Профессиональная область', alias='professionalAreaId')
    startDate: date = Field(description='Дата начала работы', alias='startDate')
    endDate: date = Field(description='Дата окончания работы', alias='endDate')
    companyName: str = Field(description='Название компании', alias='companyName')
    position: str = Field(description='Должность')
    subdivision: str = Field(description='Подразделение')
    responsibilities: Optional[Responsibility] = Field(description='Обязанности')


class Achievements(AppSmartProfileDto):
    """Схема ответа добавленного достижения к опыту внесенному вручную """
    id: UUID = Field(description='Uuid достижения')
    workExpId: str = Field(description='Id опыта работы', alias='workExpId')
    year: int = Field(description='Год достижения')
    quarter: Optional[str] = Field(description='Квартал')
    quarterInt: Optional[int] = Field(description='Номер квартала', alias='quarterInt')
    title: str = Field(description='Название достижения')
    description: str = Field(description='Описание')
    participants: Optional[list[EmployeeInAchievements]] = Field(description='Участники достижения')


class Responsibilities(AppSmartProfileDto):
    """Схема обязанностей """
    id: UUID = Field(description='Uuid обязанности')
    professionalAreaId: int = Field(description='Профессиональная область', alias='professionalAreaId')
    workExpId: str = Field(description='Id опыта работы', alias='workExpId')
    responsibilitiesText: str = Field(description='Обязанности', alias='responsibilitiesText')


class ExperienceV1(AppSmartProfileDto):
    """Схема опыта версии 1 """
    id: str = Field(description='Идентификатор опыта работы')
    title: str = Field(description='Должность')
    description: str = Field(description='Описание должность')
    period: str = Field(description='Период работы')
    achievements: Optional[list[Achievements]] = Field(description='Информация о достижениях')


class ExperienceV2(AppSmartProfileDto):
    """Схема опыта версии 2 """
    id: str = Field(description='Идентификатор опыта работы')
    position: Position = Field(description='Расположение опыта')
    header: str = Field(description='Должность')
    description: str = Field(description='Описание должность')
    responsibilities: Optional[Responsibility] = Field(description='Обязанности')
    period: str = Field(description='Период работы')
    startDate: date = Field(description='Дата начала работы', alias='startDate')
    endDate: Optional[date] = Field(description='Дата окончания работы', alias='endDate')
    experience: str = Field(description='Опыт')
    hasParticipants: bool = Field(description='Флаг наличия участников', alias='hasParticipants')
    professionalArea: ProfessionalArea = Field(description='Профессиональная область', alias='professionalArea')
    additionalInfo: Optional[list[Achievements]] = Field(description='Информация о достижениях', alias='additionalInfo')


class WorkExperienceV1(AppSmartProfileDto):
    """Схема ответа апи ios/v2/widgets/data?widgets=workExp_v1 """
    companyName: str = Field(description='Название компании', alias='companyName')
    companyLogo: Optional[str] = Field(description='Ссылка на картинку', alias='companyLogo')
    companyLogoUrl: Optional[str] = Field(description='Путь к картинке', alias='companyLogoUrl')
    experience: list[ExperienceV1] = Field(description='Список опыта')


class WorkExperienceV2(AppSmartProfileDto):
    """Схема ответа апи web/widgets/data?widgets=workExp_v2 """
    name: str = Field(description='Название компании')
    experience: str = Field(description='Опыт')
    unconfirmedExpId: Optional[int] = Field(description='Id неподтвержденного опыта работы', alias='unconfirmedExpId')
    logoLink: Optional[str] = Field(description='Ссылка на картинку', alias='logoLink')
    logoLinkUrl: Optional[str] = Field(description='Путь к картинке', alias='logoLinkUrl')
    items: list[ExperienceV2] = Field(description='Список опыта')
