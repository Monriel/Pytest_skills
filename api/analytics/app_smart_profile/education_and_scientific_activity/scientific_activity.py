""" Классы и методы для работы с api "scientific-activity" сервиса "Smart Profile" """
from requests import Response
from api.analytics.app_smart_profile.smart_profile import SmartProfile


class ScientificActivity(SmartProfile):
    """ Класс для работы с api "scientific-activity" сервиса "Smart Profile" """

    def __init__(self, type_api: str = 'web'):
        """
        Args:
            type_api: тип вызываемой api (web, api, ios/v2)
        """
        super().__init__()
        self.url = f'{self.url}/{type_api}/scientific-activity'
        self.version = '/v2' if 'ios' in self.url.split('/') else ''

    def save_scientific_activity(self, json: dict, save_activity: str, query_params: dict = None) -> Response:
        """ Отправить данные в профиль сотрудника по виджету "Научная деятельность", тип записи {activity_type}

        Args:
            query_params: параметры запроса
            json: тело запроса, содержащее информацию об ученой степени
            save_activity: тип добавляемой научной деятельности (патент, ученая степень, публикация)
        """
        return self.request(
            method='PUT',
            json=json,
            url=f'{self.url}/{save_activity}{self.version}',
            params=query_params
        )

    def get_scientific_activity_types_list(self, scientific_type: str) -> Response:
        """ Отправить запрос на получение списка типов доступных научных активностей (публикаций, ученых степеней,
            отраслей науки, патентов)

        Args:
            scientific_type: тип научной деятельности: публикации, ученые степени, отрасли науки, патенты
        """
        return self.request(method='GET', url=f'{self.url}/{scientific_type}')

    def delete_scientific_activity(self, query_params: dict, activity_type: str) -> Response:
        """ Удалить запись по научной деятельности типа {activity_type} из профиля сотрудника

        Args:
            query_params: параметры запроса (id удаляемой записи, uuid сотрудника)
            activity_type: тип научной деятельности (например, ученая степень)
        """
        return self.request(method='DELETE', url=f'{self.url}/delete{activity_type}', params=query_params)


class ScientificActivityTypes:
    """Класс для связи id с типом научной деятельности"""

    PATENT_MAPPING = {
        1: 'Изобретение',
        2: 'Полезная модель',
        3: 'Промышленный образец',
        4: 'Товарный знак, знак обслуживания, коллективный знак',
        5: 'Наименование места происхождения товара',
        6: 'Топология интегральной схемы',
        7: 'Программа для электронных вычислительных машин или база данных',
    }

    ACADEMIC_DEGREE = {
        1: 'Кандидат наук',
        2: 'Доктор наук',
        3: 'PhD'
    }

    PUBLICATION = {
        1: 'Монография',
        2: 'Научный реферат (автореферат)',
        3: 'Информативный реферат',
        4: 'Методические разработки/рекомендации',
        5: 'Тезисы докладов',
        6: 'Научная статья',
        7: 'Депонирование',
        8: 'Сборник научных трудов',
        9: 'Публикация в журналах'
    }

    SCIENCE_BRANCHES = {
        1: 'Архитектура',
        2: 'Биологические науки',
        3: 'Ветеринарные науки',
        4: 'Военные науки',
        5: 'Географические науки',
        6: 'Геолого-минералогические науки',
        7: 'Искусствоведение науки',
        8: 'Исторические науки',
        9: 'Культурология',
        10: 'Медицинские науки',
        11: 'Педагогические науки',
        12: 'Политические науки',
        13: 'Психологические',
        14: 'Сельскохозяйственные науки',
        15: 'Социологические науки',
        16: 'Теология',
        17: 'Технические науки',
        18: 'Фармацевтические науки',
        19: 'Физико-математические науки',
        20: 'Филологические науки',
        21: 'Философские науки',
        22: 'Химические науки',
        23: 'Экономические науки',
        24: 'Юридические науки',
    }
