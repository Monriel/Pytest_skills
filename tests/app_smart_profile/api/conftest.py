"""Фикстуры для работы в сервисе Smart-Profile"""
from pytest import fixture
from allure import title, step
from typing import Union, List
from _pytest.fixtures import SubRequest
from utilities.tools import find_value_from_json

from api.analytics.app_smart_profile.files import Files
from api.analytics.app_smart_profile.widgets import Widgets
from api.analytics.app_smart_profile.education_and_scientific_activity.scientific_activity import ScientificActivity
from api.analytics.app_smart_profile.characteristics.skills import Skills
from api.analytics.app_smart_profile.characteristics.languages import Languages
from api.analytics.app_smart_profile.successors import Successor
from api.analytics.app_smart_profile.employee_card.notes import Notes
from api.core_services.authentication import Authentication
from generators.enums import KeycloakGen

from generators.keycloak import get_user_data_from_keycloak as get_kc
from tests.constants import ERROR_STATUS_MSG
from users.smart_profile import EMPLOYEE_1, MANAGER_1


def make_list_of_ids(target_id: Union[str, int, List[Union[str, int]]]):
    list_of_ids: list = []
    if type(target_id) != list:
        list_of_ids.append(target_id)
    else:
        list_of_ids.extend(target_id)

    return list_of_ids


@fixture(scope="class")
@title('Фикстура. Получить данные загруженного файла')
def smart_profile_get_content_of_uploaded_file(request: SubRequest):
    """Загрузить файл в профиль"""
    user, path, type_, verify = request.param
    Authentication().get_token(user)
    response = Files().put_upload_file(
        query_params={
            'type': type_,
            'needFaceVerify': verify
        },
        file_path=f'app_smart_profile/{path}'
    )

    if response.status_code != 200:
        raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

    return response.json()


@fixture(scope='function')
@title('Удалить преемников у сотрудника')
def smart_profile_delete_successors(request: SubRequest):
    """Удалить согласованных/номинированных преемников у сотрудника"""
    appointed_successors_ids: list
    nominated_successors_ids: list
    user_uuid = get_kc(user=request.param, field=KeycloakGen.person_id)
    Authentication().get_token(MANAGER_1)

    with step('Получить список преемников у сотрудника'):
        response = Widgets().get_widget_info(
            query_params={
                'widgets': 'successor_v1',
                'userId': user_uuid
            }
        )

        if response.status_code != 200:
            raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

        widget_info_content = response.json()

    if find_value_from_json(json=widget_info_content, jp_expr='$.data[?(@.code="successor_v1")].data.items') != []:
        content = find_value_from_json(
            json=widget_info_content,
            jp_expr='$.data[?(@.code="successor_v1")].data.items[*]'
        )
        if find_value_from_json(json=widget_info_content, jp_expr='$.data[?(@.code="successor_v1")].data.totalNum') > 1:
            content = content[0]

        if 'APPOINTED' in content.values():
            appointed_id = find_value_from_json(
                json=widget_info_content,
                jp_expr='$.data[?(@.code=="successor_v1")].data.items[?(@.status=="APPOINTED")].userId'
            )

            appointed_successors_ids = make_list_of_ids(appointed_id)

            for id_ in appointed_successors_ids:
                with step(f'Удалить преемника с id = {id_}'):
                    response = Successor().decline_successor(
                        query_params={'targetUserId': user_uuid},
                        decline_type='delete',
                        successor_id=id_
                    )

                    if response.status_code != 200:
                        raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

        if 'NOMINATED' in content.values():
            nominated_id = find_value_from_json(
                json=widget_info_content,
                jp_expr='$.data[?(@.code=="successor_v1")].data.items[?(@.status=="NOMINATED")].userId'
            )

            nominated_successors_ids = make_list_of_ids(nominated_id)

            for id_ in nominated_successors_ids:
                with step(f'Отклонить преемника с id = {id_}'):
                    response = Successor().decline_successor(
                        query_params={'targetUserId': user_uuid},
                        decline_type='reject',
                        successor_id=id_
                    )

                    if response.status_code != 200:
                        raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))


@fixture(scope='function')
@title('Номинировать/согласовать преемника сотруднику')
def smart_profile_add_successors(request: SubRequest):
    """Номинировать/согласовать преемника сотруднику"""
    mapping_params = {
        'appoint': 'targetUserId',
        'nominate': 'userId'
    }
    for elem in request.param:
        auth_api, user, successor, action_type, readiness = elem
        Authentication().get_token(auth_api)

        with step(f'{mapping_params[action_type]} преемника сотруднику'):
            response = Successor(type_api='web').change_successor_request(
                query_params={mapping_params[action_type]: get_kc(user=user, field=KeycloakGen.person_id)},
                json={'readiness': readiness},
                action_type=action_type,
                successor_id=get_kc(user=successor, field=KeycloakGen.person_id)
            )

            if response.status_code != 200:
                raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))


@fixture(scope='function')
@title('Удалить научную деятельность для пользователя')
def smart_profile_delete_all_added_scientific_activity(request: SubRequest):
    scientific_activity_dict: dict = {}
    old_degree_ids: list
    old_publication_ids: list
    old_patent_ids: list
    root: str = 'data[?(@.code="scientificActivity")]..groups'
    Authentication().get_token(request.param)

    with step('Получить список старых записей в разделе научная деятельность'):
        response = Widgets().get_widget_info(query_params={'widgets': 'scientificActivity'})

        if response.status_code != 200:
            raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

        content = response.json()

        if find_value_from_json(json=content, jp_expr=f'$.{root}[?(@.tagCode="degree")].totalCount') != 0:
            old_degree_id = find_value_from_json(json=content, jp_expr=f'$.{root}[?(@.tagCode="degree")]..id')
            old_degree_ids = make_list_of_ids(old_degree_id)
            scientific_activity_dict['AcademicDegree'] = old_degree_ids

        if find_value_from_json(json=content, jp_expr=f'$.{root}[?(@.tagCode="publication")].totalCount') != 0:
            old_publication_id = find_value_from_json(
                json=content,
                jp_expr=f'$.{root}[?(@.tagCode="publication")]..id'
            )
            old_publication_ids = make_list_of_ids(old_publication_id)
            scientific_activity_dict['Publication'] = old_publication_ids

        if find_value_from_json(json=content, jp_expr=f'$.{root}[?(@.tagCode="patent")].totalCount') != 0:
            old_patent_id = find_value_from_json(json=content, jp_expr=f'$.{root}[?(@.tagCode="patent")]..id')
            old_patent_ids = make_list_of_ids(old_patent_id[::2])
            scientific_activity_dict['Patent'] = old_patent_ids

        for activity in scientific_activity_dict.keys():
            for id in scientific_activity_dict[activity]:
                with step(f'Удалить {activity} с id {id}'):
                    response = ScientificActivity(type_api='ios/v2').delete_scientific_activity(
                        query_params={'id': id},
                        activity_type=activity
                    )

                    if response.status_code != 200:
                        raise Exception(
                            f'Удаление записи с id={id} не было произведено.'
                            f' Код статуса ответа отличен от 200: {response.status_code}'
                        )


@fixture(scope='function')
@title('Фикстура. Удалить ранее добавленные "Навыки"')
def smart_profile_delete_all_skills(request: SubRequest):
    """Удалить все навыки у пользователя"""
    user = request.param[0]
    Authentication().get_token(user)
    with step(f'Получить список навыков у {user}'):
        person_id = get_kc(user=user, field=KeycloakGen.person_id)
        response = Widgets(type_api='web').get_data_widget_info_by_uuid(
            query_params={'userId': person_id},
            widget='skill_v2'
        )

        if response.status_code != 200:
            raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

        if find_value_from_json(json=response.json(), jp_expr='$.data..skills'):
            with step(f'Удалить навык у {user}'):
                response = Skills(type_api='web').update_skills(
                    query_params={'userId': person_id},
                    json={'skills': []}
                )

                if response.status_code != 200:
                    raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))


@fixture(scope='function')
@title('Фикстура. Удалить ранее добавленные "Иностранные языки"')
def smart_profile_delete_all_languages(request: SubRequest):
    """Удалить все иностранные языки у пользователя"""
    user = request.param[0]
    Authentication().get_token(user)
    languages_ids: list

    with step(f'Получить список иностранных языков у {user}'):
        person_id = get_kc(user=user, field=KeycloakGen.person_id)
        response = Widgets().get_widget_info(
            query_params={
                'userId': person_id,
                'widgets': 'language'
            })

        if response.status_code != 200:
            raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

        if find_value_from_json(json=(content := response.json()), jp_expr='$.data..data.items') != []:
            languages_id = find_value_from_json(json=content, jp_expr='$.data..data..name.key')
            languages_ids = make_list_of_ids(languages_id)

            for id_ in languages_ids:
                with step(f'Удалить иностранный язык с id = {id_} у {user}'):
                    response = Languages().delete_languages(
                        query_params={
                            'id': id_,
                            'userId': person_id
                        }
                    )

                    if response.status_code != 200:
                        raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))


@fixture(scope='function')
@title('Фикстура. Получить Id навыка по его названию')
def smart_profile_get_skill_id_by_name(request: SubRequest):
    """Получить id навыка по названию"""
    skill_name = request.param
    Authentication().get_token(EMPLOYEE_1)
    response = Skills(type_api='web').skill_search(
        query_params={
            'query': skill_name,
            'maxCount': 5
        }
    )

    if response.status_code != 200:
        raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

    return find_value_from_json(
        json=response.json(),
        jp_expr=f'$.data[?(@.title=={str.title(skill_name)})].dictSkillKey'
    )


@fixture(scope='function')
@title('Фикстура. Удалить все заметки у сотрудника')
def smart_profile_delete_all_notes(request: SubRequest):
    page_count: int = 0
    user_uuids: list
    author_uuid = get_kc(user=request.param, field=KeycloakGen.person_id)
    Authentication().get_token(request.param)

    with step('Получить количество страниц заметок по сотруднику'):
        response = Notes().get_my_notes(
            query_params={
                'authorId': author_uuid,
                'page': 0,
                'size': 3
            }
        )
        if response.status_code != 200:
            raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

        page_count = find_value_from_json(json=(content := response.json()), jp_expr=f'$.data.pageCount')

    if content['data']['notes'] != []:
        user_uuid = find_value_from_json(json=content, jp_expr=f'$.data.notes..userId')
        user_uuids = make_list_of_ids(user_uuid)

        for page_number in range(1, page_count):
            response = Notes().get_my_notes(
                query_params={
                    'authorId': author_uuid,
                    'page': page_number,
                    'size': 3
                }
            )
            if response.status_code != 200:
                raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))

            user_uuids.extend(find_value_from_json(json=response.json(), jp_expr=f'$.data.notes..userId'))

        for uuid in user_uuids:
            with step(f'Удалить заметку по сотруднику с uuid {uuid}'):
                response = Notes().delete_my_notes(
                    query_params={
                        'userId': uuid,
                        'authorId': author_uuid
                    }
                )
                if response.status_code != 200:
                    raise Exception(ERROR_STATUS_MSG.format(code=response.status_code))
