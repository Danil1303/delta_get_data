from flask import Flask, request
import requests
import threading
import time
from waitress import serve
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# URL API
url = ''
# Логин и пароль для базовой авторизации
username = ''
password = ''

# Список с данными
data = []


def get_data_from_site():
    global data
    # Отправляем GET-запрос с базовой авторизацией
    response = requests.get(url, auth=HTTPBasicAuth(username, password), headers={"Content-Type": "application/json"},
                            allow_redirects=False)

    # Проверяем, был ли запрос успешным
    if response.status_code == 200:
        data = [i['grz'] for i in response.json()]
    else:
        print(f"Ошибка: {response.status_code}")
    print(data)


def periodic_data_update():
    while True:
        get_data_from_site()
        time.sleep(300)


thread = threading.Thread(target=periodic_data_update)
thread.daemon = True
thread.start()


# Обработчик маршрута /get_status
@app.route('/get_status', methods=['GET'])
def get_status():
    # Получаем параметр 'request_number' из URL
    request_number = request.args.get('number')

    if request_number is None:
        return "Number parameter is required", 400

    # Проходим по данным и ищем номер
    for number in data:
        if request_number in number:
            return '1'
    else:
        return '0'


if __name__ == '__main__':
    # Запускаем сервер на всех интерфейсах, на 5000 порту
    serve(app, host='0.0.0.0', port=5001)
