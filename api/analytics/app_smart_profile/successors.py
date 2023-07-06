""" Классы и методы для работы с api "successors" сервиса "Smart Profile" """
from requests import Response

from api.analytics.app_smart_profile.smart_profile import SmartProfile


class Successor(SmartProfile):
    """ Класс для работы с api "successors" сервиса "Smart Profile" """

    def __init__(self, type_api: str = 'web'):
        """
        Args:
            type_api: тип вызываемой api (web, api)
        """
        super().__init__()
        self.url = f'{self.url}/{type_api}/successors'

    def get_user_info_for_successor(self, query_params: dict) -> Response:
        """ Получить данные сотрудника, для кого является преемником

        Args:
            query_params: параметры запроса
        """
        return self.request(method='GET', params=query_params, url=f'{self.url}/v2/for')

    def get_list_of_recommended_successors(self, query_params: dict) -> Response:
        """ Получить список рекомендованных преемников

        Args:
            query_params: параметры запроса
        """
        return self.request(method='GET', params=query_params, url=f'{self.url}/recommendedSuccessors')

    def search_for_successor(self, query_params: dict) -> Response:
        """ Отправить запрос на поиск преемника. Получает информацию о преемнике и его доступности

        Args:
            query_params: параметры запроса (query, size, targetUserId)
        """
        return self.request(method='GET', params=query_params, url=f'{self.url}/search')

    def decline_successor(self, decline_type: str, successor_id: str, query_params: dict,
                          json: dict = None) -> Response:
        """ Отправить запрос на отклонение или удаление заявки добавления преемника

        Args:
            json: тело с причиной отклонения
            decline_type: тип отклонения заявки (reject/delete)
            successor_id: uuid преемника
            query_params: параметры запросы (targetUserId)
        """
        return self.request(
            method='POST',
            json=json,
            params=query_params,
            url=f'{self.url}/{successor_id}/{decline_type}'
        )

    def change_successor_request(self, action_type: str, successor_id: str, json: dict, query_params: dict) -> Response:
        """ Отправить запрос на изменение данных о преемнике

        Args:
            action_type: тип изменений (appoint/nominate/readiness)
            successor_id: uuid преемника
            json: тело запроса
            query_params: параметры запроса
        """
        return self.request(
            method='POST',
            json=json,
            params=query_params,
            url=f'{self.url}/{successor_id}/{action_type}'
        )

    def get_list_of_rejection_reasons(self) -> Response:
        """ Получить список причин отклонения номинированного преемник"""
        return self.request(method='GET', url=f'{self.url}/reject')

