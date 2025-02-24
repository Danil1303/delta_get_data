import time
import logging
import requests
import threading

from waitress import serve
from flask import Flask, request
from requests.auth import HTTPBasicAuth

# Настройка логирования
logging.basicConfig(filename='log.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

with open('credentials.txt', 'r') as file:
    # Проходим по строкам файла
    for line in file:
        # Убираем лишние пробелы и проверяем каждую строку
        line = line.strip()
        # URL API
        if line.startswith('url='):
            url = line.split('=')[1]
        # Логин и пароль для базовой авторизации
        elif line.startswith('username='):
            username = line.split('=')[1]
        elif line.startswith('password='):
            password = line.split('=')[1]

# Список с данными
data = []


def get_data_from_site():
    global data
    try:
        # Отправляем GET-запрос с базовой авторизацией
        response = requests.get(url, auth=HTTPBasicAuth(username, password),
                                headers={"Content-Type": "application/json"},
                                allow_redirects=False)

        # Проверяем, был ли запрос успешным
        if response.status_code == 200:
            data = [i['grz'] for i in response.json()]
        else:
            logging.error(f'Произошла ошибка: {response.status_code}')
    except Exception as e:
        logging.error(f'Произошла ошибка: {e}')


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
