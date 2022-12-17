import pytest
from main import uploader
import requests


def test_in_status_cod():
    res = uploader.create_folder()

    #201 Наша папка успешно создана
    assert res == 201   or  res == 409  
    # Сообщение о том что папка уже существует тоже устроит


def test_search_folder():
    
    my_list = []

    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = uploader.authorization()
    params = {"path": 'disk:/'}
    res = requests.get(url=url, headers=headers, params=params).json()

    len_ = len(res["_embedded"]['items'])
    for i in range(0, len_ - 1):
        my_list.append(res["_embedded"]['items'][i]['name'])
    assert uploader.path in my_list  # Убеждаемся что в списке файлов есть наша папка