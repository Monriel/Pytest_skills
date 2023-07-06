from allure import epic, feature, story, title, step, link, dynamic
from pytest import mark
from utilities.tools import find_value_from_json, get_link
from generators.date import get_datetime_with_offset
from generators.keycloak import get_user_data_from_keycloak as get_kc

from api.analytics.app_smart_profile.education_and_scientific_activity.scientific_activity import ScientificActivity, \
    ScientificActivityTypes
from api.analytics.app_smart_profile.education_and_scientific_activity.education import Education
from api.analytics.app_smart_profile.widgets import Widgets
from api.analytics.app_smart_profile.files import Files
from tests.analytics.allure_constants import AppSmartProfileApi
from api.analytics.app_smart_profile.countries import Countries
from generators.enums import KeycloakGen
from tests.constants import ERROR_STATUS_MSG, ERROR_SUCCESS_MSG
from users.smart_profile import EMPLOYEE_1, EMPLOYEE_2


@mark.dpm
@mark.education_and_scientific_activity
@mark.scientific_activity
@mark.usefixtures('set_up')
@story('Образование и научная деятельность. Научная деятельность')
class TestScientificActivity(AppSmartProfileApi):
    employee_2_id: str
    web_patent_ids: list = []
    ios_patent_ids: list = []
    web_publication_ids: list = []
    ios_publication_ids: list = []
    web_academic_degree_ids: list = []
    ios_academic_degree_ids: list = []
    patent_mapping = {
        'web': web_patent_ids,
        'ios/v2': ios_patent_ids
    }
    publication_mapping = {
        'web': web_publication_ids,
        'ios/v2': ios_publication_ids
    }
    academic_degree_mapping = {
        'web': web_academic_degree_ids,
        'ios/v2': ios_academic_degree_ids
    }

    @staticmethod
    def set_up():
        TestScientificActivity.employee_1_id = get_kc(user=EMPLOYEE_1, field=KeycloakGen.person_id)
        TestScientificActivity.employee_2_id = get_kc(user=EMPLOYEE_2, field=KeycloakGen.person_id)

    @mark.prom
    @link(*get_link(test=10841))
    @title('Получить список доступных типов патентов')
    @mark.parametrize('auth_api', [EMPLOYEE_1], indirect=["auth_api"])
    def test_get_list_of_patent_types(self, auth_api: str):
        response = ScientificActivity(type_api='ios/v2').get_scientific_activity_types_list(
            scientific_type='patent-types'
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG

        for key, value in ScientificActivityTypes.PATENT_MAPPING.items():
            assert find_value_from_json(json=content, jp_expr=f'$.data[?(@.key = {key})].value') == value

    @mark.prom
    @link(*get_link(test=10839))
    @title('Получить список доступных типов академической степени')
    @mark.parametrize('auth_api', [EMPLOYEE_1], indirect=["auth_api"])
    def test_get_list_of_academic_degree_types(self, auth_api: str):
        response = ScientificActivity(type_api='ios/v2').get_scientific_activity_types_list(
            scientific_type='academic-degree-types'
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG

        for key, value in ScientificActivityTypes.ACADEMIC_DEGREE.items():
            assert find_value_from_json(json=content, jp_expr=f'$.data[?(@.key = {key})].value') == value

    @mark.prom
    @link(*get_link(test=10840))
    @title('Получить список доступных типов публикаций')
    @mark.parametrize('auth_api', [EMPLOYEE_1], indirect=["auth_api"])
    def test_get_list_of_publication_types(self, auth_api: str):
        response = ScientificActivity(type_api='ios/v2').get_scientific_activity_types_list(
            scientific_type='publication-types'
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG

        for key, value in ScientificActivityTypes.PUBLICATION.items():
            assert find_value_from_json(json=content, jp_expr=f'$.data[?(@.key = {key})].value') == value

    @mark.prom
    @link(*get_link(test=26150))
    @title('Получить список доступных типов отраслей наук')
    @mark.parametrize('auth_api', [EMPLOYEE_1], indirect=["auth_api"])
    def test_get_list_of_science_branches_types(self, auth_api: str):
        response = ScientificActivity(type_api='ios/v2').get_scientific_activity_types_list(
            scientific_type='science-branches'
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert (content := response.json())['success'], ERROR_SUCCESS_MSG

        for key, value in ScientificActivityTypes.SCIENCE_BRANCHES.items():
            assert find_value_from_json(json=content, jp_expr=f'$.data[?(@.key = {key})].value') == value

    @mark.prom
    @title('Получить дату окончания первого базового образования')
    @link(*get_link(test=26406))
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_first_education_date(self, auth_api: str):
        response = Education().get_first_education_date(
            query_params={'userId': TestScientificActivity.employee_2_id}
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert response.json()['success'], ERROR_SUCCESS_MSG

    @mark.prom
    @title('Получить список стран')
    @link(*get_link(test=25240))
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    def test_get_list_of_countries(self, auth_api: str):
        response = Countries().get_countries()
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
        assert response.json()['success'], ERROR_SUCCESS_MSG

    @title('Добавить патент и сохранить его id')
    @mark.parametrize(
        'smart_profile_delete_all_added_scientific_activity, auth_api, type_api, test_link',
        [
            (EMPLOYEE_1, EMPLOYEE_1, 'web', 46422),
            (EMPLOYEE_2, EMPLOYEE_2, 'ios/v2', 46421)
        ],
        indirect=['smart_profile_delete_all_added_scientific_activity', 'auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_save_scientific_activity(
            self,
            smart_profile_delete_all_added_scientific_activity: str,
            auth_api: str,
            type_api: str,
            test_link: int
    ):
        dynamic.link(*get_link(test=test_link))
        root = 'data[?(@.code="scientificActivity")]..groups'

        for type_number in ScientificActivityTypes.PATENT_MAPPING:
            with step('Добавить патент'):
                dict_json = {
                    "endDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=True),
                    "typeId": type_number,
                    "name": f"Патент типа № {type_number}",
                    "number": f"{type_number}",
                    "countryKey": "Россия",
                    "countryId": "Россия",
                    "issueDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=False)
                }

                if type_api == 'ios/v2':
                    dict_json.pop("countryId")

                response = ScientificActivity(type_api=type_api).save_scientific_activity(
                    json=dict_json,
                    save_activity='savePatent'
                )
                assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                assert response.json()['success'], ERROR_SUCCESS_MSG

            with step('Сохранить id добавленного патента'):
                response = Widgets().get_widget_info(
                    query_params={'widgets': 'scientificActivity'}
                )
                assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                assert (content := response.json())['success'], ERROR_SUCCESS_MSG
                TestScientificActivity.patent_mapping[type_api].append(
                    find_value_from_json(
                        json=content,
                        jp_expr=f'$.{root}[?(@.tagCode=="patent")].items[?(@.name=="Патент типа № {type_number}")].id'
                    )
                )

    @link(*get_link(test=46425))
    @title('Удалить патент')
    @mark.parametrize('auth_api, type_api', [(EMPLOYEE_1, 'web'), (EMPLOYEE_2, 'ios/v2')], indirect=['auth_api'])
    def test_delete_patent(self, auth_api: str, type_api: str):
        for patent_id in TestScientificActivity.patent_mapping[type_api]:
            response = ScientificActivity(type_api='ios/v2').delete_scientific_activity(
                query_params={'id': patent_id},
                activity_type='Patent'
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

    @title('Добавить учёную степень и сохранить её id')
    @mark.parametrize(
        'smart_profile_delete_all_added_scientific_activity, auth_api, type_api, test_link',
        [
            (EMPLOYEE_1, EMPLOYEE_1, 'web', 46423),
            (EMPLOYEE_2, EMPLOYEE_2, 'ios/v2', 46424)
        ],
        indirect=['smart_profile_delete_all_added_scientific_activity', 'auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_save_academic_degree(
            self,
            smart_profile_delete_all_added_scientific_activity: str,
            auth_api: str,
            type_api: str,
            test_link:int
    ):
        dynamic.link(*get_link(test=test_link))
        root = 'data[?(@.code="scientificActivity")]..groups'

        for type_degree in ScientificActivityTypes.ACADEMIC_DEGREE:
            for type_branches in ScientificActivityTypes.SCIENCE_BRANCHES:
                with step('Добавить ученую степень'):
                    response = ScientificActivity(type_api=type_api).save_scientific_activity(
                        json={
                            "issueDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=False),
                            "typeId": type_degree,
                            "dissertationName": f"Степень типа № {type_degree} с отраслью {type_branches}",
                            "university": "МГУ",
                            "branchOfScienceId": type_branches
                        },
                        save_activity='saveAcademicDegree'
                    )
                    assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                    assert response.json()['success'], ERROR_SUCCESS_MSG

                    with step('Сохранить id ученой степени'):
                        response = Widgets().get_widget_info(
                            query_params={'widgets': 'scientificActivity'}
                        )
                        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                        assert (content := response.json())['success'], ERROR_SUCCESS_MSG
                        TestScientificActivity.academic_degree_mapping[type_api].append(
                            find_value_from_json(
                                json=content,
                                jp_expr=f'$.{root}[?(@.tagCode=="degree")].items[?(@.dissertationName=="Степень '
                                        f'типа № {type_degree} с отраслью {type_branches}")].id'
                            )
                        )

    @link(*get_link(test=46479))
    @title('Удалить учёную степень')
    @mark.parametrize('auth_api, type_api', [(EMPLOYEE_1, 'web'), (EMPLOYEE_2, 'ios/v2')], indirect=['auth_api'])
    def test_delete_academic_degree(self, auth_api: str, type_api: str):
        for academic_degree in TestScientificActivity.academic_degree_mapping[type_api]:
            response = ScientificActivity(type_api='ios/v2').delete_scientific_activity(
                query_params={'id': academic_degree},
                activity_type='AcademicDegree'
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

    @title('Добавить публикацию и сохранить её id')
    @mark.parametrize(
        'smart_profile_delete_all_added_scientific_activity, auth_api, type_api, test_link',
        [
            (EMPLOYEE_1, EMPLOYEE_1, 'web', 46481),
            (EMPLOYEE_2, EMPLOYEE_2, 'ios/v2', 46480)
        ],
        indirect=['smart_profile_delete_all_added_scientific_activity', 'auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_save_publication(
            self,
            smart_profile_delete_all_added_scientific_activity: str,
            auth_api: str,
            type_api: str,
            test_link: int
    ):
        dynamic.link(*get_link(test=test_link))
        root = 'data[?(@.code="scientificActivity")]..groups'

        for type_publication in ScientificActivityTypes.PUBLICATION:
            with step('Добавить публикацию'):
                response = ScientificActivity(type_api=type_api).save_scientific_activity(
                    json={
                        "issueDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=False),
                        "typeId": type_publication,
                        "name": f"Публикация типа № {type_publication}",
                        "link": {
                            "name": f"Публикация типа № {type_publication}",
                            "url": "https://jira.sberbank.ru/"
                        }
                    },
                    save_activity='savePublication'
                )
                assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                assert response.json()['success'], ERROR_SUCCESS_MSG

                with step('Сохранить id публикации'):
                    response = Widgets().get_widget_info(
                        query_params={'widgets': 'scientificActivity'}
                    )
                    assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                    assert (content := response.json())['success'], ERROR_SUCCESS_MSG
                    TestScientificActivity.publication_mapping[type_api].append(
                        find_value_from_json(
                            json=content,
                            jp_expr=f'$.{root}[?(@.tagCode=="publication")].items'
                                    f'[?(@.name=="Публикация типа № {type_publication}")].id'
                        )
                    )

    @link(*get_link(test=46482))
    @title('Удалить публикацию')
    @mark.parametrize('auth_api, type_api', [(EMPLOYEE_1, 'web'), (EMPLOYEE_2, 'ios/v2')], indirect=['auth_api'])
    def test_delete_publication(self, auth_api: str, type_api: str):
        for publication in TestScientificActivity.publication_mapping[type_api]:
            response = ScientificActivity(type_api='ios/v2').delete_scientific_activity(
                query_params={'id': publication},
                activity_type='Publication'
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG

    @mark.dependency(name='save_publication_with_certificate')
    @title('Добавить публикацию c сертификатом')
    @mark.parametrize(
        'smart_profile_get_content_of_uploaded_file',
        [[EMPLOYEE_1, "certificate.jpeg", "scientific_publication_certificate", "undefined"]],
        indirect=True
    )
    @mark.parametrize(
        'smart_profile_delete_all_added_scientific_activity, auth_api, type_api, test_link',
        [
            (EMPLOYEE_1, EMPLOYEE_1, 'web', 46486),
            (EMPLOYEE_1, EMPLOYEE_1, 'ios/v2', 46485)
        ],
        indirect=['smart_profile_delete_all_added_scientific_activity', 'auth_api'],
        ids=['web', 'ios/v2']
    )
    def test_save_publication_with_certificate(
            self,
            smart_profile_get_content_of_uploaded_file: dict,
            smart_profile_delete_all_added_scientific_activity: str,
            auth_api: str,
            type_api: str,
            test_link: int
    ):
        dynamic.link(*get_link(test=test_link))
        content = smart_profile_get_content_of_uploaded_file
        root = 'data[?(@.code="scientificActivity")]..groups'
        TestScientificActivity.publication_mapping[type_api] = []

        with step('Добавить публикацию c сертификатом'):
            response = ScientificActivity(type_api=type_api).save_scientific_activity(
                json={
                    "issueDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=False),
                    "typeId": 1,
                    "name": f"Публикацию c сертификатом в {type_api}",
                    "link": {
                        "name": f"Публикацию c сертификатом в {type_api}",
                        "url": "https://jira.sberbank.ru/"
                    },
                    "certificates": content['data']
                },
                save_activity='savePublication'
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG
            TestScientificActivity.url_uploaded_file = find_value_from_json(json=content, jp_expr='$.data..targetUrl')
            TestScientificActivity.name_uploaded_file = find_value_from_json(json=content, jp_expr='$.data..fileName')

            with step('Сохранить id публикации'):
                response = Widgets().get_widget_info(
                    query_params={'widgets': 'scientificActivity'}
                )
                assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                assert (content_widget_info := response.json())['success'], ERROR_SUCCESS_MSG
                TestScientificActivity.publication_mapping[type_api].append(
                    find_value_from_json(
                        json=content_widget_info,
                        jp_expr=f'$.{root}[?(@.tagCode=="publication")].items'
                                f'[?(@.name=="Публикацию c сертификатом в {type_api}")].id'
                    )
                )

            with step('Добавить публикацию c сертификатом в профиль коллеге (негативный)'):
                userId = TestScientificActivity.employee_2_id
                response = ScientificActivity(type_api=type_api).save_scientific_activity(
                    query_params={'userId': userId},
                    json={
                        "issueDate": get_datetime_with_offset(fmt="%Y-%m-%d", weeks=52, to_the_future=False),
                        "typeId": 1,
                        "name": f"Публикацию c сертификатом в {type_api}",
                        "link": {
                            "name": f"Публикацию c сертификатом в {type_api}",
                            "url": "https://jira.sberbank.ru/"
                        },
                        "certificates": content['data']
                    },
                    save_activity='savePublication'
                )
                assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
                assert (content := response.json())['success'] == False
                assert content['status'] == "INTERNAL_SERVER_ERROR"
                assert content['error']['code'] == 403
                assert content['error']['message'] == f"Permissions denied:  [EDIT_WIDGET_DATA]. Target user: {userId}"

    @title('Скачать сертификат публикации')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    @mark.dependency(depends=['save_publication_with_certificate'])
    @link(*get_link(test=46503))
    def test_download_publication_certificate(self, auth_api: str):
        response = Files().get_download_file(
            query_params={
                'url': TestScientificActivity.url_uploaded_file,
                'fileName': TestScientificActivity.name_uploaded_file
            }
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)

    @title('Скачать сертификат иностранного языка в профиле коллеги')
    @mark.parametrize('auth_api', [EMPLOYEE_2], ids=['colleague'], indirect=True)
    @mark.dependency(depends=['save_publication_with_certificate'])
    @link(*get_link(test=46502))
    def test_download_publication_certificate_from_colleague(self, auth_api: str):
        response = Files().get_download_file(
            query_params={
                'url': f'{TestScientificActivity.url_uploaded_file}{TestScientificActivity.employee_1_id}',
                'fileName': TestScientificActivity.name_uploaded_file
            }
        )
        assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)

    @title('Удалить публикацию с сертификатом в своем профиле')
    @mark.parametrize('auth_api', [EMPLOYEE_1], ids=['EMPLOYEE_1'], indirect=True)
    @mark.dependency(depends=['save_publication_with_certificate'])
    @link(*get_link(test=46501))
    def test_delete_publication_with_certificate(self, auth_api: str):
        for publication in TestScientificActivity.publication_mapping['ios/v2']:
            response = ScientificActivity(type_api='ios/v2').delete_scientific_activity(
                query_params={'id': publication},
                activity_type='Publication'
            )
            assert response.status_code == 200, ERROR_STATUS_MSG.format(code=response.status_code)
            assert response.json()['success'], ERROR_SUCCESS_MSG
