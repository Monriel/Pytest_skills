""" Класс и методы для работы с файлами сервиса "Smart Profile" """
from requests import Response

from utilities.config import Config
from api.analytics.app_smart_profile.smart_profile import SmartProfile


class Files(SmartProfile):
    """ Класс для работы с файлами сервиса "Smart Profile" """

    def __init__(self):
        super().__init__()
        self.url = f'{self.url}/web'

    def put_upload_file(self, query_params: dict, file_path: str) -> Response:
        """ Отправить запрос на загрузку файла

        Args:
            query_params: параметры запроса
            file_path: BinaryIO файл для загрузки
        """
        file_name = file_path.split('/')[-1]
        self.headers.pop('Content-Type')
        with (Config.test_data_dir / file_path).open(mode='rb') as file:
            return self.request(
                method='PUT',
                url=f'{self.url}/files/upload',
                params=query_params,
                files={'files': (file_name, file.read())}
            )

    def get_download_file(self, query_params: dict) -> Response:
        """ Отправить запрос на скачивание файла

        Args:
            query_params: параметры запроса
        """
        return self.request(method='GET', params=query_params, url=f'{self.url}/downloadFile')
