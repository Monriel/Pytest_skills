""" Классы и методы для работы с api "work-experience" сервиса "Smart Profile" """
from requests import Response

from api.analytics.app_smart_profile.smart_profile import SmartProfile


class WorkExperience(SmartProfile):
    """ Класс для работы с web-api "work-experience" сервиса "Smart Profile" """

    def __init__(self, type_api: str = 'web'):
        """
        Args:
            type_api: тип вызываемой api (web, api)
        """
        super().__init__()
        self.url = f'{self.url}/{type_api}/work-experience'

    def add_workexp_achievement(self, workexp_id: str, json: dict, query_params: dict = None) -> Response:
        """ Добавить запись о достижении в виджет "Опыт работы", где {workexp_id} - id записи об опыте работы

        Args:
            workexp_id: id опыта работы
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(method='POST', json=json, params=query_params, url=f'{self.url}/{workexp_id}/achievements')

    def change_workexp_achievement(self, achievement_id, workexp_id, json: dict, query_params: dict = None) -> Response:
        """ Изменить запись о достижении в виджете "Опыт работы"

        Args:
            achievement_id: id изменяемого достижения
            workexp_id: id опыта работы
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(
            method='PUT',
            json=json,
            params=query_params,
            url=f'{self.url}/{workexp_id}/achievements/{achievement_id}'
        )

    def delete_workexp_achievements(self, achievement_id: str, query_params: dict = None) -> Response:
        """ Удалить запись о достижении в виджете "Опыт работы" (workExp)

        Args:
            achievement_id: id записи о достижении
            query_params: параметры запроса
        """
        return self.request(method='DELETE', params=query_params, url=f'{self.url}/achievements/{achievement_id}')

    def add_unconfirmed_work_experience(self, json: dict, query_params: dict = None) -> Response:
        """ Добавить запись о неподтвержденном опыте работы в виджете "Опыт работы"

        Args:
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(method='POST', json=json, params=query_params, url=f'{self.url}/unconfirmed/v1/company')

    def edit_unconfirmed_work_experience(self, json: dict, query_params: dict = None) -> Response:
        """ Редактировать запись о неподтвержденном опыте работы в виджете "Опыт работы"

        Args:
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(method='PUT', json=json, params=query_params, url=f'{self.url}/unconfirmed/v1/company')

    def delete_unconfirmed_work_experience(self, json: dict, query_params: dict = None) -> Response:
        """ Удалить запись о неподтвержденном опыте работы виджет "Опыт работы"

        Args:
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(method='DELETE', json=json, params=query_params, url=f'{self.url}/unconfirmed/v1/company')

    def get_professional_area(self) -> Response:
        """ Получить список профессиональных областей в неподтвержденном опыте работы"""
        return self.request(method='GET', url=f'{self.url}/unconfirmed/v1/professional-area')

    def add_responsibilities(self, json: dict, query_params: dict = None) -> Response:
        """ Добавить обязанности к подтвержденному опыту работы

        Args:
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(method='POST', json=json, params=query_params, url=f'{self.url}/custom-info/v1/')

    def edit_responsibilities(self, json: dict, query_params: dict = None) -> Response:
        """ Редактировать обязанности к подтвержденному опыту работы

        Args:
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(method='PUT', json=json, params=query_params, url=f'{self.url}/custom-info/v1/')

    def delete_responsibilities(self, json: dict, query_params: dict = None) -> Response:
        """ Удалить обязанности к подтвержденному опыту работы

        Args:
            json: тело запроса, содержащее информацию о достижении
            query_params: параметры запроса
        """
        return self.request(
            method='DELETE',
            json=json,
            params=query_params,
            url=f'{self.url}/custom-info/v1/responsibilities'
        )
