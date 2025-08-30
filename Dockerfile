# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Создаем виртуальное окружение и ставим зависимости
RUN python -m venv --copies /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Устанавливаем рабочее окружение PATH
ENV PATH="/opt/venv/bin:$PATH"

# Команда запуска бота
CMD ["python", "bot.py"]
