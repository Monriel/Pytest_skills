from allure import epic, feature, story, title, step, link
from pytest import mark
from utilities.tools import find_value_from_json, get_link
from generators.date import get_datetime_with_offset
from generators.randoms import get_random_string
from utilities import model

from api.analytics.app_smart_profile.experience_and_achievements.work_experience import WorkExperience
from dto.app_smart_profile.template.work_experience import PROFESSIONAL_AREA
from dto.app_smart_profile.schema.work_experience import Company, Achievements, Responsibilities, WorkExperienceV1, \
    WorkExperienceV2
from api.analytics.app_smart_profile.widgets import Widgets
from tests.analytics.allure_constants import AppSmartProfileApi
from generators.enums import KeycloakGen
from generators.keycloak import get_user_data_from_keycloak as get_kc
from tests.constants import ERROR_STATUS_MSG, ERROR_SUCCESS_MSG
from users.smart_profile import EMPLOYEE_1


@mark.dpm
@mark.experience_and_achievements
@mark.work_achievements
@mark.usefixtures('set_up')
@story('Опыт и достижения. Достижения к опыту работы')
class TestWorkExperience(AppSmartProfileApi):
    employee_person_id: str
    last_work_experience_id: str
    achievement_id: str
    unconfirmed_id: str
    unconfirmed_exp_id: str
    work_exp_custom_info_id: str
    last_work_exp_custom_info_id: str

    @staticmethod
    def set_up():
        TestWorkExperience.employee_person_id = get_kc(user=EMPLOYEE_1, field=KeycloakGen.person_id)

    @link(*get_link(test=46533))
    @title('Получить список профессиональных областей')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_professional_area(self, auth_api):
        response = WorkExperience(type_api='api').get_professional_area()
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert content['data'] == PROFESSIONAL_AREA

    @link(*get_link(test=46466))
    @title('Добавить опыт работы внесенный вручную')
    @mark.parametrize(
        'smart_profile_delete_unconfirmed_work_experience, auth_api',
        [(EMPLOYEE_1, EMPLOYEE_1)],
        indirect=True
    )
    def test_add_unconfirmed_work_experience(self, smart_profile_delete_unconfirmed_work_experience, auth_api):
        for professional_area_id in range(1, 3):
            response = WorkExperience(type_api='api').add_unconfirmed_work_experience(
                json={
                    "position": get_random_string(length=15),
                    "subdivision": get_random_string(length=15),
                    "responsibilities": {
                        "text": get_random_string(length=250)
                    },
                    "startDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=False),
                    "endDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=5, to_the_future=False),
                    "companyName": f"Рога и копыта № {professional_area_id}",
                    "professionalAreaId": professional_area_id
                }
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert content['status'] == "CREATED"
            assert model.is_valid(response=content['data'], model=Company)

    @link(*get_link(test=46465))
    @title('Редактировать опыт работы внесенный вручную')
    @mark.parametrize(
        'smart_profile_delete_unconfirmed_work_experience,  smart_profile_add_unconfirmed_work_experience, auth_api',
        [(EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_1)],
        indirect=True
    )
    def test_edit_unconfirmed_work_experience(
            self,
            smart_profile_delete_unconfirmed_work_experience,
            smart_profile_add_unconfirmed_work_experience,
            auth_api
    ):
        unconfirmed_exp_id, work_exp_custom_info_id = smart_profile_add_unconfirmed_work_experience
        response = WorkExperience(type_api='api').edit_unconfirmed_work_experience(
            json={
                "position": "Старший менеджер",
                "subdivision": "ВСП",
                "responsibilities": {
                    "text": "Обязанности после редактирования",
                    "workExpCustomInfoId": work_exp_custom_info_id
                },
                "startDate": "2022-05-01",
                "endDate": "2023-05-01",
                "companyName": f"Рога и копыта",
                "professionalAreaId": 2,
                "unconfirmedExpId": unconfirmed_exp_id
            }
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert content['status'] != "CREATED"
        assert content['status'] == "OK"
        assert model.is_valid(response=content['data'], model=Company)

    @link(*get_link(test=46469))
    @title('Добавить достижение к опыту работы внесенного вручную')
    @mark.parametrize(
        'smart_profile_delete_unconfirmed_work_experience,  smart_profile_add_unconfirmed_work_experience, auth_api',
        [(EMPLOYEE_1, EMPLOYEE_1, EMPLOYEE_1)],
        indirect=True
    )
    def test_add_work_achievement_to_unconfirmed_work(
            self,
            smart_profile_delete_unconfirmed_work_experience,
            smart_profile_add_unconfirmed_work_experience,
            auth_api
    ):
        TestWorkExperience.unconfirmed_exp_id, TestWorkExperience.work_exp_custom_info_id \
            = smart_profile_add_unconfirmed_work_experience

        with step('Получить id опыта работы внесенного вручную'):
            response = Widgets().get_widget_info(query_params={'widgets': 'workExp_v2'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            TestWorkExperience.unconfirmed_id = find_value_from_json(
                json=content,
                jp_expr=f'$.data[?(@.code=="workExp_v2")].data.items'
                        f'[?(@.unconfirmedExpId=={TestWorkExperience.unconfirmed_exp_id})]..positionId'
            )

        with step('Добавить достижение к опыту работы внесенного вручную без параметра "unconfirmedExpId"'):
            response = WorkExperience().add_workexp_achievement(
                query_params={'userId': TestWorkExperience.employee_person_id},
                json={
                    'name': "Название достижения",
                    'description': "Описание",
                    'year': "2022",
                    'quarter': 4,
                    'participants': []
                },
                workexp_id=TestWorkExperience.unconfirmed_id
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'] == False
            assert content['status'] == "INTERNAL_SERVER_ERROR"
            assert content['error']['code'] == 400
            assert content['error']['message'] == f"Опыт работы не найден: идентификатор " \
                                                  f"{TestWorkExperience.unconfirmed_id}"

        with step('Добавить достижение к опыту работы внесенного вручную'):
            response = WorkExperience().add_workexp_achievement(
                query_params={'userId': TestWorkExperience.employee_person_id},
                json={
                    'unconfirmedExpId': TestWorkExperience.unconfirmed_exp_id,
                    'name': "Название достижения",
                    'description': "Описание",
                    'year': "2022",
                    'quarter': 4,
                    'participants': []
                },
                workexp_id=TestWorkExperience.unconfirmed_id
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert model.is_valid(response=content['data'], model=Achievements)
            TestWorkExperience.achievement_id = find_value_from_json(json=content, jp_expr='$.data.id')

    @link(*get_link(test=46470))
    @title('Редактировать добавленное достижение к опыту работы внесенного вручную')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_edit_added_work_achievementt_to_unconfirmed_work(self, auth_api):
        with step('Редактировать достижение к опыту работы внесенного вручную без параметра "unconfirmedExpId"'):
            response = WorkExperience().change_workexp_achievement(
                json={
                    'name': "Название достижения",
                    'description': "Описание",
                    'year': "2022",
                    'quarter': 1,
                    'participants': []
                },
                workexp_id=TestWorkExperience.unconfirmed_id,
                achievement_id=TestWorkExperience.achievement_id
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'] == False
            assert content['status'] == "INTERNAL_SERVER_ERROR"
            assert content['error']['code'] == 500
            assert content['error']['message'] == f"Не удалось найти достижение: " \
                                                  f"{TestWorkExperience.achievement_id}"

            with step('Редактировать достижение к опыту работы внесенного вручную'):
                response = WorkExperience().change_workexp_achievement(
                    json={
                        'unconfirmedExpId': TestWorkExperience.unconfirmed_exp_id,
                        'name': "Название достижения после редактирования",
                        'description': "Описание после редактирования",
                        'year': "2022",
                        'quarter': 2,
                        'participants': []
                    },
                    workexp_id=TestWorkExperience.unconfirmed_id,
                    achievement_id=TestWorkExperience.achievement_id
                )
                assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                assert response.json()['success'], ERROR_SUCCESS_MSG

    @link(*get_link(test=46473))
    @title('Редактирование обязанности добавленного к подтвержденному опыту работы')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_edit_responsibilities(self, auth_api):
        with step('Получить id последнего места работы'):
            response = Widgets().get_widget_info(query_params={'widgets': 'workExp_v2'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            TestWorkExperience.last_work_experience_id = find_value_from_json(
                json=content,
                jp_expr='$.data[?(@.code="workExp_v2")]..items[0]..items[0].id'
            )
            TestWorkExperience.last_work_exp_custom_info_id = find_value_from_json(
                json=content,
                jp_expr='$.data[?(@.code="workExp_v2")]..items[0]..items[0]..workExpCustomInfoId'
            )

        with step('Редактировать обязанности к последнему месту работы'):
            response = WorkExperience(type_api='api').edit_responsibilities(
                json={
                    'id': TestWorkExperience.last_work_exp_custom_info_id,
                    'workExpId': TestWorkExperience.last_work_experience_id,
                    'responsibilitiesText': "Тестирование профиля сотрудника после редактирования",
                    'professionalAreaId': 1
                }
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert model.is_valid(response=content['data'], model=Responsibilities)

    @link(*get_link(test=46464))
    @title('Весь опыт работы (от кадрового источника и введенный вручную) (work_exp_v2)')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_work_exp_v2(self, auth_api):
        response = Widgets().get_widget_info(query_params={'widgets': 'workExp_v2'})
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        content_exp_v2 = find_value_from_json(json=content, jp_expr='$.data[?(@.code=="workExp_v2")].data.items[*]')
        assert model.is_valid(response=content_exp_v2[0], model=WorkExperienceV2)

    @link(*get_link(test=46471))
    @title('Удалить добавленное достижение к опыту работы внесенного вручную')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_delete_added_work_achievement(self, auth_api):
        with step('Удалить достижение к опыту работы внесенного вручную'):
            response = WorkExperience().delete_workexp_achievements(
                query_params={"isUnconfirmedWorkExp": True},
                achievement_id=TestWorkExperience.achievement_id
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

        with step('Проверить удаление достижения к опыту работы внесенного вручную'):
            response = Widgets().get_widget_info(query_params={'widgets': 'workExp_v2'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG

            assert find_value_from_json(
                json=content,
                jp_expr=f'$.data[?(@.code == "workExp_v2")].data.items'
                        f'[?(@.unconfirmedExpId == {TestWorkExperience.unconfirmed_exp_id})]..additionalInfo') == []

    @link(*get_link(test=46474))
    @title('Удалить добавленные обязанности к последнему месту работы')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_delete_added_responsibilities(self, auth_api):
        with step('Удалить добавленные обязанности'):
            response = WorkExperience(type_api='api').delete_responsibilities(
                json={'workExpCustomInfoId': TestWorkExperience.last_work_exp_custom_info_id}
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

        with step('Проверить удаление обязанности и сохранение тега'):
            response = Widgets().get_widget_info(query_params={'widgets': 'workExp_v2'})
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert (content := response.json())['success'], ERROR_SUCCESS_MSG
            assert find_value_from_json(
                json=content,
                jp_expr='$.data[?(@.code="workExp_v2")]..items[0]..items[0]..professionalArea.id'
            ) == 1
            assert 'text' not in find_value_from_json(
                json=content,
                jp_expr='$.data[?(@.code="workExp_v2")]..items[0]..items[0]..responsibilities'
            )

    @link(*get_link(test=46684))
    @title('Создание достижения для подтвержденного опыта в web')
    @mark.parametrize(
        'smart_profile_delete_all_added_achievements, auth_api',
        [(EMPLOYEE_1, EMPLOYEE_1)],
        indirect=True
    )
    def test_add_work_achievement_web(self, smart_profile_delete_all_added_achievements, auth_api):
        response = WorkExperience(type_api='web').add_workexp_achievement(
            json={
                'name': "Достижение для подтвержденного опыта",
                'description': "Достиг всех высот",
                'year': "2022",
                'quarter': 4,
                'participants': []
            },
            workexp_id=TestWorkExperience.last_work_experience_id
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert model.is_valid(response=content['data'], model=Achievements)
        TestWorkExperience.achievement_id = find_value_from_json(json=content, jp_expr='$.data.id')

    @link(*get_link(test=46683))
    @title('Редактировать добавленное достижение к последнему месту работы в web')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_edit_added_work_achievement_web(self, auth_api):
        response = WorkExperience(type_api='web').change_workexp_achievement(
            json={
                'name': "Достижение для подтвержденного опыта в вебе",
                'description': "Достиг всех высот",
                'year': "2022",
                'quarter': 1,
                'participants': [f"{TestWorkExperience.employee_person_id}"]
            },
            workexp_id=TestWorkExperience.last_work_experience_id,
            achievement_id=TestWorkExperience.achievement_id
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert model.is_valid(response=content['data'], model=Achievements)

    @link(*get_link(test=46685))
    @title('Удалить добавленное достижение к последнему месту работы')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_delete_added_work_achievement_web(self, auth_api):
        response = WorkExperience().delete_workexp_achievements(achievement_id=TestWorkExperience.achievement_id)
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert response.json()['success'], ERROR_SUCCESS_MSG

    @link(*get_link(test=46694))
    @title('Создание достижения для подтвержденного опыта в ios')
    @mark.parametrize(
        'smart_profile_delete_all_added_achievements, auth_api',
        [(EMPLOYEE_1, EMPLOYEE_1)],
        indirect=True
    )
    def test_add_work_achievement_ios(self, smart_profile_delete_all_added_achievements, auth_api):
        response = WorkExperience(type_api='ios/v2').add_workexp_achievement(
            json={
                'name': "Достижение 2 для подтвержденного опыта",
                'description': "Достиг всех высот в ios",
                'year': "2022",
                'quarter': 3,
                'participants': []
            },
            workexp_id=TestWorkExperience.last_work_experience_id
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        assert model.is_valid(response=content['data'], model=Achievements)
        TestWorkExperience.achievement_id = find_value_from_json(json=content, jp_expr='$.data.id')

    @link(*get_link(test=46695))
    @title('Редактировать добавленное достижение к последнему месту работы в ios')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_edit_added_work_achievement_ios(self, auth_api):
        response = WorkExperience(type_api='ios/v2').change_workexp_achievement(
            json={
                'name': "Достижение 2 для подтвержденного опыта в ios",
                'description': "Достиг всех высот",
                'year': "2022",
                'quarter': 1,
                'participants': [f"{TestWorkExperience.employee_person_id}"]
            },
            workexp_id=TestWorkExperience.last_work_experience_id,
            achievement_id=TestWorkExperience.achievement_id
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert response.json()['success'], ERROR_SUCCESS_MSG

    @link(*get_link(test=46822))
    @title('Весь опыт работы (от кадрового источника и введенный вручную) (work_exp_v1)')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_work_exp_v1(self, auth_api):
        response = Widgets(type_api='ios/v2').get_widget_info(query_params={'widgets': 'workExp_v1'})
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
        content_exp_v1 = find_value_from_json(json=content, jp_expr='$.data[?(@.code=="workExp_v1")].data[*]')
        assert model.is_valid(response=content_exp_v1[0], model=WorkExperienceV1)
