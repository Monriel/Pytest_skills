from utilities.tools import find_value_from_json
from allure import epic, feature, story, title, step, link, dynamic
from pytest import mark
from utilities.tools import get_link

from api.analytics.app_smart_profile.successors import Successor
from tests.analytics.allure_constants import AppSmartProfileApi
from api.analytics.app_smart_profile.widgets import Widgets
from generators.enums import KeycloakGen, PersonGen
from generators.keycloak import get_user_data_from_keycloak as get_kc
from generators.person import get_data_from_segment
from tests.constants import ERROR_STATUS_MSG, ERROR_SUCCESS_MSG
from users.smart_profile import MANAGER_1, EMPLOYEE_1, EMPLOYEE_2, EMPLOYEE_3, EMPLOYEE_4, EMPLOYEE_5


@mark.dpm
@mark.successors
@mark.usefixtures('set_up')
@story('Преемники')
class TestSuccessors(AppSmartProfileApi):
    employee_id: str
    successor_id: str

    @staticmethod
    def set_up():
        TestSuccessors.employee_id = get_kc(user=EMPLOYEE_1, field=KeycloakGen.person_id)
        TestSuccessors.successor_id = get_kc(user=EMPLOYEE_2, field=KeycloakGen.person_id)

    @title('Добавить номинированного преемника сотруднику')
    @mark.parametrize('smart_profile_delete_successors', [EMPLOYEE_1], indirect=True)
    @mark.parametrize(
        'auth_api, type_api, user, successor, readiness, test_link',
        [
            (EMPLOYEE_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 'NOW', 10843),
            (EMPLOYEE_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 'YEAR', 45028)
        ],
        indirect=['auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_add_nominated_successor(self, smart_profile_delete_successors, auth_api, type_api, user, successor,
                                     readiness, test_link):
        dynamic.link(*get_link(test=test_link))
        response = Successor(type_api=type_api).change_successor_request(
            query_params={'userId': get_kc(user=user, field=KeycloakGen.person_id)},
            json={'readiness': readiness},
            action_type='nominate',
            successor_id=get_kc(user=successor, field=KeycloakGen.person_id)
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert content['data'] == 'NOMINATED'

    @link(*get_link(test=45336))
    @title('Получить данные пользователя для кого является преемником')
    @mark.parametrize('auth_api', [EMPLOYEE_2], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_user_info_for_successor(self, auth_api):
        response = Successor(type_api='api').get_user_info_for_successor(
            query_params={'userId': TestSuccessors.employee_id}
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert response.json()['success'], ERROR_SUCCESS_MSG

    @link(*get_link(test=27161))
    @title('Получить список рекомендованных преемников')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_list_of_recommended_successors(self, auth_api):
        response = Successor().get_list_of_recommended_successors(query_params={'userId': TestSuccessors.employee_id})
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)

    @title('Найти преемника с заданными параметрами для сотрудника')
    @mark.parametrize(
        'smart_profile_delete_successors, auth_api, type_api, user, successor, test_link',
        [
            (EMPLOYEE_1, EMPLOYEE_1, 'web', EMPLOYEE_1, MANAGER_1, 23230),
            (EMPLOYEE_1, EMPLOYEE_1, 'ios/v2', EMPLOYEE_1, MANAGER_1, 45134)
        ],
        indirect=['smart_profile_delete_successors', 'auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_get_search_for_successor(self, smart_profile_delete_successors, auth_api, type_api, user, successor,
                                      test_link):
        dynamic.link(*get_link(test=test_link))
        response = Successor(type_api=type_api).search_for_successor(
            query_params={
                'size': 100,
                'query': 'Name',
                'targetUserId': get_kc(user=user, field=KeycloakGen.person_id)
            }
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert response.json()['success'], ERROR_SUCCESS_MSG

    @title('Изменить готовность преемника')
    @mark.parametrize(
        'smart_profile_delete_successors,'
        'smart_profile_add_successors',
        [
            (
                    EMPLOYEE_1,
                    [
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_2, 'nominate', 'NOW'),
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_3, 'nominate', 'YEAR')
                    ]
            )
        ],
        indirect=True
    )
    @mark.parametrize(
        'auth_api, type_api, user, successor, readiness, test_link',
        [
            (EMPLOYEE_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 'YEAR', 26408),
            (EMPLOYEE_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 'NOW', 45186)
        ],
        indirect=['auth_api']
    )
    def test_change_readiness_successor(self, smart_profile_delete_successors, smart_profile_add_successors, auth_api,
                                        type_api, user, successor, readiness, test_link):
        dynamic.link(*get_link(test=test_link))
        successor_uuid = get_kc(user=successor, field=KeycloakGen.person_id)
        successor_name = get_data_from_segment(user=successor, field=PersonGen.firstname)

        with step('Изменить готовность преемника'):
            response = Successor(type_api=type_api).change_successor_request(
                query_params={'targetUserId': get_kc(user=user, field=KeycloakGen.person_id)},
                json={'readiness': readiness},
                action_type='readiness',
                successor_id=successor_uuid
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

        with step('Проверить изменение готовности преемника'):
            response = Widgets(type_api=type_api).get_widget_info(query_params={'widgets': 'successor_v1'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert find_value_from_json(
                json=content,
                jp_expr=f'$.data..items[?(@.firstName=="{successor_name}")].userId'
            ) == successor_uuid
            assert find_value_from_json(
                json=content,
                jp_expr=f'$.data..items[?(@.firstName=="{successor_name}")].status'
            ) == 'NOMINATED'
            assert find_value_from_json(
                json=content,
                jp_expr=f'$.data..items[?(@.firstName=="{successor_name}")].readiness'
            ) == readiness

    @title('Удалить сотрудником/руководителем номинированного/согласованного преемника')
    @mark.parametrize(
        'smart_profile_delete_successors,'
        'smart_profile_add_successors',
        [
            (
                    EMPLOYEE_1,
                    [
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_2, 'nominate', 'NOW'),
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_3, 'nominate', 'YEAR'),
                        (MANAGER_1, EMPLOYEE_1, EMPLOYEE_4, 'appoint', 'NOW'),
                        (MANAGER_1, EMPLOYEE_1, EMPLOYEE_5, 'appoint', 'YEAR')
                    ]
            )
        ],
        indirect=True
    )
    @mark.parametrize(
        'auth_api, type_api, user, successor, test_link',
        [
            (EMPLOYEE_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 23231),
            (EMPLOYEE_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 45187),
            (MANAGER_1, 'web', EMPLOYEE_1, EMPLOYEE_4, 45340),
            (MANAGER_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_5, 45187)
        ],
        indirect=['auth_api']
    )
    def test_delete_successor(self, smart_profile_delete_successors, smart_profile_add_successors, auth_api,
                              type_api, user, successor, test_link):
        dynamic.link(*get_link(test=test_link))
        successor_uuid = get_kc(user=successor, field=KeycloakGen.person_id)

        with step(f'Удалить преемника (тип апи = {type_api})'):
            response = Successor(type_api=type_api).decline_successor(
                query_params={'targetUserId': get_kc(user=user, field=KeycloakGen.person_id)},
                decline_type='delete',
                successor_id=successor_uuid
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

        with step(f'Проверить удаленного преемника (тип апи = {type_api})'):
            response = Widgets(type_api=type_api).get_widget_info(query_params={'widgets': 'successor_v1'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert successor_uuid not in find_value_from_json(json=content, jp_expr=f'$.data..items')

    @title('Удалить сотрудником согласованного преемника (негативный)')
    @mark.parametrize(
        'smart_profile_delete_successors,'
        'smart_profile_add_successors',
        [
            (
                    EMPLOYEE_1,
                    [
                        (MANAGER_1, EMPLOYEE_1, EMPLOYEE_2, 'appoint', 'NOW'),
                        (MANAGER_1, EMPLOYEE_1, EMPLOYEE_3, 'appoint', 'YEAR')
                    ]
            )
        ],
        indirect=True
    )
    @mark.parametrize(
        'auth_api, type_api, user, successor, test_link',
        [
            (EMPLOYEE_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 45344),
            (EMPLOYEE_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 45343),
        ],
        indirect=['auth_api']
    )
    def test_delete_appointed_successor_by_employee(self, smart_profile_delete_successors, smart_profile_add_successors,
                                                    auth_api, type_api, user, successor, test_link):
        dynamic.link(*get_link(test=test_link))
        successor_uuid = get_kc(user=successor, field=KeycloakGen.person_id)

        with step(f'Сотрудник удаляет согласованного преемника (тип апи = {type_api})'):
            response = Successor(type_api=type_api).decline_successor(
                query_params={'targetUserId': get_kc(user=user, field=KeycloakGen.person_id)},
                decline_type='delete',
                successor_id=successor_uuid
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'] == False
            assert content['status'] == "INTERNAL_SERVER_ERROR"
            assert content['error']['code'] == 403

        with step(f'Проверить наличие преемника (тип апи = {type_api})'):
            response = Widgets(type_api=type_api).get_widget_info(query_params={'widgets': 'successor_v1'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert successor_uuid not in find_value_from_json(json=content, jp_expr=f'$.data..items')

    @title('Добавить согласованных преемников сотруднику')
    @mark.parametrize('smart_profile_delete_successors', [EMPLOYEE_1], indirect=True)
    @mark.parametrize(
        'auth_api, type_api, user, successor, readiness, test_link',
        [
            (MANAGER_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 'NOW', 27161),
            (MANAGER_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 'YEAR', 45194)
        ],
        indirect=['auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_add_appointed_successor(self, smart_profile_delete_successors, auth_api,
                                     type_api, user, successor, readiness, test_link):
        dynamic.link(*get_link(test=test_link))
        successor_uuid = get_kc(user=successor, field=KeycloakGen.person_id)
        successor_name = get_data_from_segment(user=successor, field=PersonGen.firstname)
        user_uuid = get_kc(user=user, field=KeycloakGen.person_id)

        with step(f'Добавить согласованного преемника (тип апи = {type_api})'):
            response = Successor(type_api=type_api).change_successor_request(
                query_params={'targetUserId': user_uuid},
                json={'readiness': readiness},
                action_type='appoint',
                successor_id=successor_uuid
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert content['data'] == 'APPOINTED'

        with step(f'Проверить добавление согласованного преемника (тип апи = {type_api})'):
            response = Widgets(type_api=type_api).get_widget_info(
                query_params={
                    'widgets': 'successor_v1',
                    'userId': user_uuid
                }
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert find_value_from_json(
                json=content,
                jp_expr=f'$.data..items[?(@.firstName=="{successor_name}")].userId'
            ) == successor_uuid

    @title('Отклонить руководителем номинированного преемника у сотрудника')
    @mark.parametrize(
        'smart_profile_delete_successors,'
        'smart_profile_add_successors',
        [
            (
                    EMPLOYEE_1,
                    [
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_2, 'nominate', 'NOW'),
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_3, 'nominate', 'YEAR')
                    ]
            )
        ],
        indirect=True
    )
    @mark.parametrize('reason_number', [1, 2, 3, 4])
    @mark.parametrize(
        'auth_api, type_api, user, successor, test_link',
        [
            (MANAGER_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 45346),
            (MANAGER_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 45345)
        ],
        indirect=['auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_reject_successor_by_manager(self, smart_profile_delete_successors, smart_profile_add_successors,
                                         reason_number, auth_api, type_api, user, successor, test_link):
        dynamic.link(*get_link(test=test_link))
        successor_uuid = get_kc(user=successor, field=KeycloakGen.person_id)
        user_uuid = get_kc(user=user, field=KeycloakGen.person_id)

        with step(f'Отклонить руководителем номинированного преемника (тип апи = {type_api})'):
            response = Successor(type_api=type_api).decline_successor(
                query_params={'targetUserId': get_kc(user=user, field=KeycloakGen.person_id)},
                json={
                    'answerId': reason_number,
                    'comment': "test"
                },
                decline_type='reject',
                successor_id=successor_uuid
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

        with step(f'Проверить отклонение преемника (тип апи = {type_api})'):
            response = Widgets(type_api=type_api).get_widget_info(
                query_params={
                    'widgets': 'successor_v1',
                    'userId': user_uuid
                }
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert successor_uuid not in find_value_from_json(json=content, jp_expr=f'$.data..items')

    @title('Открыть руководителем задачу на согласование преемника')
    @mark.parametrize(
        'smart_profile_delete_successors,'
        'smart_profile_add_successors',
        [
            (
                    EMPLOYEE_1,
                    [
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_2, 'nominate', 'NOW'),
                        (EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_3, 'nominate', 'YEAR')
                    ]
            )
        ],
        indirect=True
    )
    @mark.parametrize(
        'auth_api, type_api, user, successor, test_link',
        [
            (MANAGER_1, 'web', EMPLOYEE_1, EMPLOYEE_2, 45450),
            (MANAGER_1, 'ios/v2', EMPLOYEE_1, EMPLOYEE_3, 45449)
        ],
        indirect=['auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_open_successors_task_by_manager(self, smart_profile_delete_successors, smart_profile_add_successors,
                                             auth_api, type_api, user, successor, test_link):
        dynamic.link(*get_link(test=test_link))
        successor_uuid = get_kc(user=successor, field=KeycloakGen.person_id)
        successor_name = get_data_from_segment(user=successor, field=PersonGen.firstname)

        response = Widgets(type_api=type_api).get_data_widget_info_by_uuid(
            query_params={'userId': get_kc(user=user, field=KeycloakGen.person_id)},
            widget='successor_v1'
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert find_value_from_json(
            json=content,
            jp_expr=f'$.data..items[?(@.firstName=="{successor_name}")].userId'
        ) == successor_uuid

    @title('Получить список причин отклонения номинированного преемника')
    @mark.parametrize(
        'smart_profile_delete_successors,'
        'smart_profile_add_successors',
        [(EMPLOYEE_1, [(EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_2, 'nominate', 'NOW')])],
        indirect=True
    )
    @mark.parametrize('auth_api', [MANAGER_1], indirect=['auth_api'], ids=['web'])
    @link(*get_link(test=45454))
    def test_get_list_of_rejection_reasons(self, smart_profile_delete_successors, smart_profile_add_successors,
                                           auth_api):
        reasons_name = [
            "недостаточно профессиональных знаний и навыков",
            "не подходит по личностным характеристикам",
            "не подходит по масштабу управления",
            "другое"
        ]
        reasons_ids = [1, 2, 3, 4]
        response = Successor(type_api='web').get_list_of_rejection_reasons()
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        for reason in response.json():
            assert reason['answer'] in reasons_name, f'{reason["answer"]} такой причины нет в списке'
            assert reason['answerId'] in reasons_ids, f'{reason["answerId"]} такого id нет в списке'
