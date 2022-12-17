import json
from pprint import pprint
import requests
import datetime

def read_line(atrib):
    with open('token.txt', 'rt', encoding='utf-8' ) as file:
        for line in file:
            if line.split('=')[0] == atrib:
                return line.split('=')[1].strip()
        
def create_json(data, file_name):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open(file_name, 'wt', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"{file_name} создан")


class Get_vk():
    def __init__(self, access_token, vk_id):
        self.vk_id = vk_id
        self.access_token = access_token
    
    def get_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {
        'access_token': self.access_token,
        'user_ids': self.vk_id,  
        'v': '5.131'}
        res = requests.get(url, params=params).json()
        print(res['response'][0]['first_name']+" "+res['response'][0]['last_name'])

    def get_photos(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {
        'access_token': self.access_token,
        'owner_id': self.vk_id,
        'album_id': 'profile', 
        'extended': '1',   
        'v': '5.131'}
        res = requests.get(url, params=params).json()
        return res



class YaUploader:
    def __init__(self, token, path):
        self.token = token
        self.path = path

    def authorization(self):
        return {
        'Content-Type': 'application/json',
        'Authorization': f'OAuth {self.token}'}

    def connect_check(self):
        url = 'https://cloud-api.yandex.net/v1/disk'
        headers = self.authorization()
        res = requests.get(url=url, headers=headers)
        if res.status_code == 200:
            return 'ok'
        else:
            return res

    def create_folder(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.authorization()
        params = {"path": self.path}
        res = requests.put(url=url, headers=headers, params=params)

        # return res.status_code
        if res.status_code <= 201:
            print(f"Директория \"{self.path}\" успешно создона")
            # return res.status_code
        elif res.status_code == 409:
            print(f"Папка \"{self.path}\" уже существует")
            # return res.status_code
        else:
            print(f"Ошибка \"{res.json()['message']}\"")
        
        return res.status_code


    def upload_photos(self, photo_name, photo_url):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.authorization()
        params = {
        'path': f'disk:/{self.path}/{photo_name}',
        'url':photo_url}
        res = requests.post(url=url, headers=headers, params=params)

        if res.status_code <= 202:
            print(f'Фото {photo_name} успешно загружено')
        else:
            print(f"Ошибка \"{res.json()['message']}\"")


def vk_json_processing():
    
    data = get_vk.get_photos()
    
    if 'response' in data:
        get_vk.get_info()
        count = data['response']['count']
        print(str(count)+" фото")

        new_json = []
        name_list = []
        photo_dict = {}

        for photo in data['response']['items']:
            max_width = 0
            if str(photo['likes']['count']) in name_list:
                name_list.append(str(photo['likes']['count'])+"-"+str(photo['date']))
            else:
                name_list.append(str(photo['likes']['count']))

            for size in photo['sizes']:
                if size['width'] >= max_width:
                    max_width = size['width']
                    type_size = size['type']
                    src = size['url']
            photo_dict['file_name'] = name_list[-1]
            photo_dict['size'] = type_size
           
            new_json.append( { 'url': src, 'param': photo_dict.copy() } )
    
        return {'count': count, 'files':new_json}

    elif 'error' in data:
        print(f"""Код ошибки:  {data['error']['error_code']} \n{data['error']['error_msg']}""")

           

# vk_id = input("Введите id: ")
vk_id = read_line('default_id') # if vk_id=='' else vk_id


# token = str(input("Введите токен Ya.Диск: "))
token = read_line('ya_token') # if token=='' else token


get_vk = Get_vk(read_line('vk_service_id'), vk_id)
uploader = YaUploader(token, 'Мои фоточки из вк')

if uploader.connect_check() == 'ok':
    photos = vk_json_processing()
    if photos != None:
        if photos['count'] > int(read_line('default_count_photo')):
            count_photo = int(read_line('default_count_photo'))
        else:
            count_photo = photos['count']

        print(f"сохроняем {count_photo} фото")

        data = []

        res = uploader.create_folder()
        if res == 201 or res == 409:
            for photo in range(0, int(count_photo)):
                uploader.upload_photos(photos['files'][photo]['param']['file_name']+'.jpeg', photos['files'][photo]['url'])
                data.append(photos['files'][photo]['param']) 
        create_json(data, 'files.json')    
        print("Завершено")
else:
    print(f"Ошибка {uploader.connect_check().status_code}\n{uploader.connect_check().json()['message']}")