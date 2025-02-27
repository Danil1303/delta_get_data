# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем только необходимые файлы в контейнер
COPY main.py credentials.txt requirements.txt /app/

# Устанавливаем зависимости, если они есть
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем скрипт
CMD ["python", "main.py"]
