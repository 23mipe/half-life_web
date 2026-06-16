# half-life_web
Веб-версия справочника по игре Half-Life.


# Требования
- Python 3.8 (или выше)
- flask 3.1.3
- pillow 12.2.0
- bcrypt 5.0.0
- reportlab 4.5.1
- psycopg2-binary 2.9.12
- gunicorn 23.0.0


# Технологии
- Хостинг: Vercel.com
- Backend: Flask (Python)
- Frontend: HTML5, CSS3 (без JavaScript)
- База данных: Neon.com, PostgreSQL
- Хранение сессий: Flask session + PostgreSQL
- Движок шаблонов: Jinja


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
