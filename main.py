from core import *

vk_access_token = ""
version = "5.131"

print('Backup foto VK in Ya disk.\n/help - список команд\n/q - выход')
backup = BackupFotoVkInYaDisk(vk_access_token, version)
backup.authorization()
while True:
    command = input("Введите команду:\n")
    if command == "/auth":
        backup = BackupFotoVkInYaDisk(vk_access_token, version)
        backup.authorization()
    elif command == "/ga":
        backup.albums()
    elif command == "/сf":
        backup.photos()
    elif command == "/gf":
        backup.get_list_photos()
    elif command == "/bk":
        backup.backup()
    elif command == "/cll":
        logs_clear()
        print("Логи удалены!\n")
    elif command == "/help":
        commands()
    elif command == "/q":
        logs("Выход")
        break
    else:
        logs("Не верный ввод!")
