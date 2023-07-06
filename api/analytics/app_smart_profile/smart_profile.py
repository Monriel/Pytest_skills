"""Модуль базового клиентского класса запросов к сервису app-smart_profile"""
from requests import Response

from api.custom_requests import Request
from services import Services


class SmartProfile(Request):
    """Базовый клиентский класс запросов к сервису app-smart_profile"""

    NAME = Services.APP_SMART_PROFILE

    def __init__(self):
        super().__init__()
        self.headers.update({'Content-Type': 'application/json'})
        self.url = f'{self.url}/smart-profile'

    def get_current_user(self) -> Response:
        """ Отправить GET-запрос на получение данных по текущему пользователю"""
        return self.request(method='GET', url=f'{self.url}/web/profile/current-user')
