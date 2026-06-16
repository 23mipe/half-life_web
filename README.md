# half-life_web
Веб-версия справочника по игре Half-Life.


# Требования
- Python 3.8 или выше
- Flask 3.1.3
- Pillow (опционально, для изображений)
- Bcrypt 5.0.0
- Reportlab 4.5.1
- Psycopg2-binary 2.9.12


# Технологии
- Backend: Flask (Python)
- Frontend: HTML5, CSS3 (без JavaScript)
- База данных: SQLite
- Хранение сессий: Flask session + SQLite


# Установка и запуск

bash 
# 1. Скопируйте папку с проектом
cd half-life_web (в терминале/cmd)

# 2. Установите зависимости
py -m pip install -r requirements.txt
# или вручную:
py -m pip install flask pillow bcrypt reportlab psycopg2-binary

# 3. Запустите сервер
py app.py

# 4. Откройте в браузере
http://localhost:5001


Cвободно для изучения и модификации.
txt
