from datetime import *
import requests
import json


def commands():
    logs("Список команд")
    print("""/auth - авторизация
/ga - список альбомов
/сf - создать список фото
/gf - получить список фото
/bk - сделать бекап 
/cll - очистить файл logs.txt\n""")


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def logs(name_command):
    with open("logs.txt", "a", encoding="'utf-8'") as f:
        now = datetime.now()
        print_command = ''.join(name_command)
        f.write(now.strftime('%d.%m.%Y - %H:%M') + " - " + print_command + '\n')
        print(f"{print_command}\n")


def logs_clear():
    with open("logs.txt", "w", encoding="'utf-8'"):
        pass


def photo_dict(params_vk, params):
    photo = {}
    response_photo = requests.get('https://api.vk.com/method/photos.get', params={**params_vk, **params})
    for i in response_photo.json()["response"]["items"]:
        if i["likes"]["count"] not in photo:
            photo[i["likes"]["count"]] = {i["sizes"][-1]["type"]: i["sizes"][-1]["url"]}
        else:
            photo[f"{i['likes']['count']}_{datetime.utcfromtimestamp(i['date']).strftime('%d.%m.%Y-%H.%M.%S')}"] \
                = {i["sizes"][-1]["type"]: i["sizes"][-1]["url"]}
    return photo


def count_photo_condition(vk_user_id, params_vk, album_id):
    while True:
        count_photo = input("Введите количество фото для бекапа (по умолчанию 5):\n")
        if count_photo == "":
            params = {"owner_id": vk_user_id, "album_id": album_id, "rev": 1,
                      "extended": 1, "photo_sizes": 1, "count": 5}
            photo = photo_dict(params_vk, params)
            logs("Список фото сформирован!")
            return photo
        elif count_photo.isnumeric():
            params = {"owner_id": vk_user_id, "album_id": album_id, "rev": 1,
                      "extended": 1, "photo_sizes": 1, "count": int(count_photo)}
            photo = photo_dict(params_vk, params)
            logs("Список фото сформирован!")
            return photo
        elif count_photo == "/q":
            logs("Отмена создания списка фото!")
            return {}
        else:
            logs("Ошибка количества фото!")


class BackupFotoVkInYaDisk:
    def __init__(self, vk_access_token, version):
        self.vk_access_token = vk_access_token
        self.version = version
        self.photo = {}
        vk = False
        ya = False
        print("\nАвторизация")

        while vk is False:
            self.vk_user_id = input("Введите id Вконтакте:\n")
            if self.vk_user_id == "/q":
                vk = True
            else:
                if self.vk_user_id.isnumeric():
                    self.vk_user_id = int(self.vk_user_id)
                self.params_vk = {'access_token': self.vk_access_token, 'v': self.version}
                response = requests.get('https://api.vk.com/method/users.get', params={**self.params_vk,
                                                                                       'user_ids': self.vk_user_id})
                try:
                    if self.vk_user_id == response.json()["response"][0]["id"] and \
                            response.json()['response'][0]['first_name'] != "DELETED":
                        vk = True
                        logs(f"Аккаунт найден: {response.json()['response'][0]['id']} - "
                             f"{response.json()['response'][0]['first_name']} "
                             f"{response.json()['response'][0]['last_name']}")
                    else:
                        logs(f"Найден удаленный аккаунт {self.vk_user_id}")
                except IndexError:
                    logs(f"Аккаунт {self.vk_user_id} не найден!")

        while (ya is False) and self.vk_user_id != "/q":
            self.ya_token = input("Введите токен Яндекс диска:\n")
            if self.ya_token == "/q":
                ya = True
            else:
                self.ya_headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                                   'Authorization': f'OAuth {self.ya_token}'}
                response = requests.get('https://cloud-api.yandex.net/v1/disk', headers=self.ya_headers)
                if response.status_code == 200:
                    ya = True
                    logs(f"Яндекс диск подключен: {response.json()['user']['login']}")
                else:
                    logs(f"Яндекс диск не подключен!")

    def authorization(self):
        if self.vk_user_id != "/q" and self.ya_token != "/q":
            logs("Авторизация успешна!")
        else:
            logs("Авторизация отменена!")

    def albums(self):
        if self.vk_user_id != "/q" and self.ya_token != "/q":
            params = {"need_system": 1, "owner_id": self.vk_user_id}
            response_album = requests.get('https://api.vk.com/method/photos.getAlbums',
                                          params={**self.params_vk, **params})
            logs("Cписок альбомов")
            for i in response_album.json()["response"]["items"]:
                if i['id'] != -9000:
                    print(f"id альбома: {i['id']}\nНазвание альбома: {i['title']}\n"
                          f"Количество фото в альбоме: {i['size']}\n")
        else:
            logs("/ga - Вы не авторизованы!")

    def photos(self):
        if self.vk_user_id != "/q" and self.ya_token != "/q":
            album = False
            while album is False:
                album_id = input("Введите id альбома(по умолчанию профиль):\n")
                params_test = {"owner_id": self.vk_user_id, "album_id": album_id, "count": 1}
                response_photo_test = requests.get('https://api.vk.com/method/photos.get',
                                                   params={**self.params_vk, **params_test})
                if album_id == "":
                    album = True
                    self.photo = count_photo_condition(self.vk_user_id, self.params_vk, "profile")
                elif is_number(album_id) and ("error" not in response_photo_test.json()):
                    album = True
                    self.photo = count_photo_condition(self.vk_user_id, self.params_vk, album_id)
                elif album_id == "/q":
                    logs("Отмена создания списка фото!")
                else:
                    logs("Ошибка id альбома!")
        else:
            logs("/сf - Вы не авторизованы!")

    def get_list_photos(self):
        if self.vk_user_id != "/q" and self.ya_token != "/q":
            logs("Cписок фото")
            if self.photo == {}:
                print("Список пуст!\n")
            else:
                for i in self.photo:
                    print(f"URL: {list(self.photo[i].values())[0]}\nName: {i}\n"
                          f"Size: {list(self.photo[i].keys())[0]}\n")
        else:
            logs("/gf - Вы не авторизованы!")

    def backup(self):
        if self.vk_user_id != "/q" and self.ya_token != "/q":
            if self.photo == {}:
                logs("Список фото пуст! Бекап не возможен!")
            else:
                now = datetime.now()
                directory = f"{self.vk_user_id}-{now.strftime('%d.%m.%Y-%H.%M')}"
                requests.put('https://cloud-api.yandex.net/v1/disk/resources', params={"path": directory},
                             headers=self.ya_headers)
                result = list()
                for i in self.photo:
                    requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                  params={"path": f"{directory}/{i}.jpg", "url": list(self.photo[i].values())[0]},
                                  headers=self.ya_headers)
                    result.append({"file_name": f"{i}.jpg", "size": list(self.photo[i].keys())[0]})
                with open("result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
                logs("Бекап выполнен!")
        else:
            logs("/bk - Вы не авторизованы!")
