""" Модуль содержит классы и методы для работы с api "education" сервиса "Smart Profile" """
from requests import Response

from api.analytics.app_smart_profile.smart_profile import SmartProfile


class Education(SmartProfile):
    """ Класс для работы с api "education" сервиса "Smart Profile" """

    def __init__(self, type_api: str = 'web'):
        """
        Args:

            type_api: тип вызываемой api (web, api, ios/v2)
        """
        super().__init__()
        self.url = f'{self.url}/{type_api}/education'

    def get_first_education_date(self, query_params: dict) -> Response:
        """ Отправить запрос на получение даты окончания первого образования

        Args:
            query_params: параметры запроса (userId)
        """
        return self.request(method='GET', params=query_params, url=f'{self.url}/basic/firstEducationDate')

    def post_add_extra_education(self, json: dict, query_params: dict = None) -> Response:
        """ Отправить запрос на добавление записи о дополнительном образовании

        Args:
            json: тело запроса
            query_params: параметры запроса (userId)
        """
        return self.request(method='POST', json=json, params=query_params, url=f'{self.url}/external')

    def put_change_extra_education(self, query_params: dict, json: dict, education_id: str) -> Response:
        """ Отправить запрос на изменение записи о дополнительном образовании

        Args:
            json: тело запроса
            education_id: id изменяемой записи
            query_params: параметры запроса (userId)
        """
        return self.request(method='PUT', json=json, params=query_params, url=f'{self.url}/external/{education_id}')

    def get_extra_education(self, query_params: dict, education_id: str) -> Response:
        """ Отправить запрос на получение записи о дополнительном образовании

        Args:
            education_id: id изменяемой записи
            query_params: параметры запроса (userId)
        """
        return self.request(method='GET', params=query_params, url=f'{self.url}/external/{education_id}')

    def delete_extra_education(self, education_id: str, query_params: dict = None) -> Response:
        """ Отправить запрос на удаление записи о дополнительном образовании

        Args:
            education_id: id изменяемой записи
            query_params: параметры запроса (userId)
        """
        return self.request(method='DELETE', params=query_params, url=f'{self.url}/external/{education_id}')
