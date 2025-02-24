import sys
import time
import requests
import threading

from waitress import serve
from flask import Flask, request
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
data = []


def get_data_from_delta() -> None:
    # Получает список занятых машин с сайта АС Дельта 2.0
    global data
    credentials = get_credentials({'url': '', 'username': '', 'password': ''})
    try:
        # Отправляем GET-запрос с базовой авторизацией
        response = requests.get(credentials['url'],
                                auth=HTTPBasicAuth(credentials['username'], credentials['password']),
                                headers={"Content-Type": "application/json"},
                                allow_redirects=False)

        # Проверяем, был ли запрос успешным
        if response.status_code == 200:
            data = [i['grz'] for i in response.json()]
        else:
            send_message(f'Произошла ошибка: {response.status_code}')
    except Exception as e:
        send_message(f'Произошла ошибка: {e}')


def periodic_data_update() -> None:
    while True:
        get_data_from_delta()
        time.sleep(300)


def send_message(message: str) -> None:
    credentials = get_credentials({'TOKEN': '', 'chat_id': ''})
    url = f'https://api.telegram.org/bot{credentials['TOKEN']}/sendMessage?chat_id={credentials['chat_id']}&text={message}'
    requests.get(url).json()


def get_credentials(credentials: dict[str, str]) -> dict[str, str]:
    try:
        for key in credentials.keys():
            with open('credentials.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if key in line:
                        credentials[key] = line.split('=')[1]
                        break
        return credentials
    except Exception as e:
        send_message(f'Произошла ошибка: {e}')


# Обработчик маршрута /get_status
@app.route('/get_status', methods=['GET'])
def get_status():
    global data
    if not data:
        send_message(f'Произошла ошибка: данные не получены')

    # Получаем параметр 'request_number' из URL
    request_number = request.args.get('number')

    if request_number is None:
        return 'Number parameter is required', 400

    # Проходим по данным и ищем номер
    for number in data:
        if request_number in number:
            return '1'
    else:
        return '0'


if __name__ == '__main__':
    data = []

    thread = threading.Thread(target=periodic_data_update)
    thread.daemon = True
    thread.start()

    # Запускаем сервер на всех интерфейсах, на порту 5001
    serve(app, host='0.0.0.0', port=5001)

# pyinstaller -w -F --onefile main.py
