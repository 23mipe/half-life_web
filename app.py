from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
import json
import uuid
import database as db
from datetime import datetime
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import bcrypt

app = Flask(__name__)
app.secret_key = "half_life_secret_key_2025"

db.init_db()

# ---------- Содержание в стиле Half-Life ----------
CONTENT = {
    "history": {
        "title": "Инцидент в Black Mesa",
        "text": """
            <p><strong>16 мая 200_ года</strong> — резонансный каскад в Аномальных Материалах лаборатории Black Mesa навсегда изменил мир.</p>
            <ul>
                <li><strong>Телепортация кристалла</strong> — неосторожный эксперимент доктора Гордона Фримена открыл портал в измерение Зен.</li>
                <li><strong>Вторжение</strong> — инопланетные существа (вортигонты, хедкрабы, барнаклы) хлынули в комплекс.</li>
                <li><strong>HECU</strong> — правительство отправляет морпехов для «зачистки», приказывая уничтожить всех свидетелей.</li>
                <li><strong>Спаситель</strong> — Гордон Фримен пробивается через реактор, отключив портал в Зен.</li>
                <li><strong>G-Man</strong> — таинственный мужчина в синем костюме предлагает Фримену «работу».</li>
            </ul>
            <p><em>«Правильный человек в неправильном месте может изменить всё на свете»</em> — G‑Man.</p>
        """,
        "image": "black_mesa.jpg"
    },
    "modern": {
        "title": "Оружие и враги Half‑Life",
        "text": """
            <p>Главный арсенал учёного-спасателя:</p>
            <ul>
                <li><strong>Монтировка</strong> — легендарное оружие ближнего боя, ломает ящики и вортигонтов.</li>
                <img src="/static/images/fomka.jpg" alt="Монтировка">
                <li><strong>Пистолет Glock 17</strong> — базовый ствол с 17 патронами.</li>
                <img src="/static/images/glock.jfif" alt="Glock 17">
                <li><strong>SPAS-12</strong> — дробовик с режимом двойного выстрела.</li>
                <img src="/static/images/spas.jpg" alt="SPAS-12">
                <li><strong>Ружьё MP5</strong> — автомат, имеющий подствольный гранатомёт и использующий патроны от Glock 17.</li>
                <img src="/static/images/MP5.jfif" alt="MP5">
                <li><strong>Револьвер Python</strong> — пистолет, наносящий колоссальный урон, но имеет только 6 патронов в барабане.</li>
                <img src="/static/images/python.jpg" alt="Револьвер">
                <li><strong>Арбалет</strong> — снайперская винтовка с оптикой и взрывными болтами.</li>
                <img src="/static/images/arbolet.jpg" alt="Арбалет">
                <li><strong>RPG</strong> — ракетница с наводящимся режимом, что управляется прицелом/лазером.</li>
                <img src="/static/images/rpg.jpg" alt="RPG">
                <li><strong>Тау-пушка</strong> — экспериментальное оружие, стреляет сквозь стены.</li>
                <img src="/static/images/tau.jpg" alt="Тау-пушка">
                <li><strong>Ручной улий</strong> — оружие грантов, что стреляет самонаводящимися мухами и имеет быструю стрельбу при альтернативной стрельбе.</li>
                <img src="/static/images/muha.jpg" alt="Рукоулей">
                <li><strong>Глюонная пушка</strong> — распыляет инопланетную слизь, является самым сильным оружием игры и использует патроны Тау-пушки.</li>
                <img src="/static/images/gluon.jpg" alt="Глюонная пушка">
                <li><strong>Граната</strong> — разрывная ручная гранада, чем дольше зажимаешь кнопку выстрела, тем дальше кидается.</li>
                <img src="/static/images/granata.jpg" alt="Гренада">
                <li><strong>Лазерная мина-ловушка</strong> — взрывается при контакте с лазером или при выстреле в мину.</li>
                <img src="/static/images/lasermine.jpg" alt="Лазерная Мина">
                <li><strong>Радиоуправляемая мина</strong> — взрывчатка, что взрывается при нажатии на кнопку мыши стрельбы, при альтернативной подкидывает ещё мины.</li>
                <img src="/static/images/radiomine.jpg" alt="Управляемая Мина">
                <li><strong>Снарк</strong> — самонаводящееся маленькое создание, что при отсутствии врагов кидается на игрока.</li>
                <img src="/static/images/snark.jpg" alt="Снарк">
            </ul>
            <p><strong>Интересный факт:</strong> Монтировка была добавлена в игру всего за день до релиза.</p>
        
            <h3>Противники:</h3>
            <ul>
                <li><strong>Хедкраб</strong> — прыгающий паразит, превращающий людей в зомби.</li>
                <img src="/static/images/heady.jpg" alt="Хеди">
                <li><strong>Зомби</strong> — ходящий труп, захваченный хедкрабом, если не стрелять в голову - после смерти скидывает живого хедкраба.</li>
                <img src="/static/images/zondre.jpg" alt="Зондре">
                <li><strong>Хаундай</strong> — трёхногое существо, атакующая ультразвуком по площади.</li>
                <img src="/static/images/houndie.jpg" alt="Псина">
                <li><strong>Буллсквид</strong> — двуногое создание, поедающее трупы сотрудников и стреляющаяся выделениями из рта.</li>
                <img src="/static/images/bull.jpg" alt="Булл">
                <li><strong>Вортигонт</strong> — шокирующие электричеством инопланетные рабы.</li>
                <img src="/static/images/vort.jpg" alt="Вортигонт">
                <li><strong>Барнакл</strong> — потолочная ловушка с длинным языком.</li>
                <img src="/static/images/barnacle.jpg" alt="Барнакл">
                <li><strong>Солдат HECU</strong> — хорошо вооружённый морской пехотинец, время от времени кидающий гранату.</li>
                <img src="/static/images/hecu.jpg" alt="Хеку">
                <li><strong>Вертолет HECU</strong> — летающий транспорт HECU, уязвимый только к взрывам и взрывному оружию.</li>
                <img src="/static/images/helicopter.jpg" alt="Вертолет">
                <li><strong>Гаргантюа</strong> — неуязвимое к обычным выстрелам и атакам существо, способное умереть только от ПВО или сильного заряда электричества. Никакое ваше оружие не способно ему навредить</li>
                <img src="/static/images/garga.jpg" alt="Гаргантюа">
                <li><strong>Ассасин Чёрной Оперы</strong> — быстрые уворотливые женщины-убийцы.</li>
                <img src="/static/images/assasin.jpg" alt="АССасины">
                <li><strong>Инопланетный грант</strong> — бронированные пришельцы с рукоульем как оружие.</li>
                <img src="/static/images/grunt.jpg" alt="Грант">
                <li><strong>Контроллер пришельцев</strong> — летающие пришельцы, появляющиеся под конец игры.</li>
                <img src="/static/images/controll.jpg" alt="Контроллер">
                <li><strong>Гонарч</strong> — мать всех хедкрабов и последняя стадия их развития. Является по совместительству боссом.</li>
                <img src="/static/images/gonar.jpg" alt="Гонарч">
                <li><strong>Нихилант</strong> — финальный босс игры и предвадитель расы Зен и организатор вторжения пришельцев на землю.</li>
                <img src="/static/images/nihilantus.jpg" alt="Нихилант">
            </ul>
            <p><strong>Интересный факт:</strong> В самой игре название расы Вортигонтов не упоминается, и они просто назывались 'Инопланетные рабы'. О их настоящем названии стало известно из файлов игры.</p>
        """,
        "image": "weapons.jpg"
    },
    "persons": {
        "title": "Герои Black Mesa",
        "text": """
            <p>Личности, без которых Half‑Life не стала бы легендой:</p>

            <div class="person-card">
                <img src="/static/images/gordon_freeman.png" alt="Фото Гордона Фримена" class="hero-photo">
                <h3>Гордон Фримен</h3>
                <p>Теоретический физик, выпускник MIT. Проходимец, спасший человечество от портального шторма. Награждён монтировкой и HEV-костюмом Mark IV.</p>
            </div>

            <div class="person-card">
                <img src="/static/images/isaac_kleiner.jpg" alt="Фото Айзека Кляйнера" class="hero-photo">
                <h3>Айзек Кляйнер</h3>
                <p>Близкий друг Гордона, гениальный учёный. Вместе с Эли Вэнсом строил телепорт.</p>
            </div>

            <div class="person-card">
                <img src="/static/images/eli_vans.jpg" alt="Фото Эли Вэнса" class="hero-photo">
                <h3>Илай Вэнс</h3>
                <p>Ведущий специалист по телепортации. Отец Алекс Вэнс, погибший от рук комбайна.</p>
            </div>

            <div class="person-card">
                <img src="/static/images/g_man.jpg" alt="Фото G‑Man" class="hero-photo">
                <h3>G‑Man</h3>
                <p>Таинственный «работодатель», контролирующий события во вселенной Half‑Life. Его цели неизвестны.</p>
            </div>

            <div class="person-card">
                <img src="/static/images/barney_calhoun.png" alt="Фото Барни Калхуна" class="hero-photo">
                <h3>Барни Калхун</h3>
                <p>Охранник Black Mesa, пообещавший Гордону пиво после работы. Позже боец Сопротивления.</p>
            </div>

            <p><strong>Цитата:</strong> «Они ждали тебя, Гордон... В назначенный час. Не опоздай.» — G‑Man.</p>
        """,
        "image": "gordon.jpg"
    },
    "instructions": {
        "title": "Руководство пользователя",
        "text": """
            <p>Добро пожаловать в энциклопедию вселенной Half‑Life.</p>
            <p>Этот сайт создан для фанатов и исследователей легендарной серии. Вы можете:</p>
            <ul>
                <li>Узнать <strong>причину резонансного каскада</strong> в Black Mesa</li>
                <li>Изучить <strong>полный арсенал</strong> Гордона Фримена</li>
                <li>Познакомиться с <strong>героями и злодеями</strong> игры</li>
                <li>Пройти <strong>интерактивный мастер-класс</strong> — проверьте знания о Half‑Life</li>
                <li>Оставить <strong>заметки и комментарии</strong> в личном кабинете</li>
                <li>Посмотреть <strong>историю посещений</strong> разделов</li>
            </ul>
            <p>Ваши данные сохраняются в <strong>гостевой сессии</strong> или после регистрации. Приятного погружения в мир Half‑Life!</p>
        """,
        "image": "instruction.jpg"
    }
}

# ---------- Маршруты ----------
@app.route('/')
def index():
    if 'user_id' not in session and 'guest_id' not in session:
        session['guest_id'] = str(uuid.uuid4())
        session['history'] = []
        session['notes'] = []
    return render_template('index.html', content=CONTENT)


@app.route('/section/<section_name>')
def section(section_name):
    if section_name not in CONTENT:
        return redirect(url_for('index'))

    if 'user_id' in session:
        db.add_user_history(session['user_id'], section_name)
    else:
        history = session.get('history', [])
        if section_name not in history:
            history.append(section_name)
            session['history'] = history
            db.save_session(session['guest_id'], json.dumps(history), json.dumps(session.get('notes', [])))

    return render_template('section.html', section=CONTENT[section_name], section_name=section_name)


@app.route('/guest_cabinet')
def guest_cabinet():
    section_names = {
        "history": "Инцидент в Black Mesa",
        "modern": "Оружие и враги",
        "persons": "Герои Half‑Life",
        "instructions": "Руководство",
        "masterclass": "Мастер-класс"
    }

    if 'user_id' in session:
        history_rows = db.get_user_history(session['user_id'])
        history_with_names = [(row[0], section_names.get(row[0], row[0]), row[1]) for row in history_rows]
        notes_rows = db.get_user_notes(session['user_id'])
        notes = [{'text': row[0], 'section': row[1], 'timestamp': row[2]} for row in notes_rows]
        return render_template('guest_cabinet.html', history=history_with_names, notes=notes, user=session['username'])
    else:
        history = session.get('history', [])
        notes = session.get('notes', [])
        history_with_names = [(item, section_names.get(item, item), '') for item in history]
        return render_template('guest_cabinet.html', history=history_with_names, notes=notes, user=None)


@app.route('/add_note', methods=['POST'])
def add_note():
    note_text = request.form.get('note', '').strip()
    section_name = request.form.get('section', 'general')
    if note_text:
        if 'user_id' in session:
            db.add_user_note(session['user_id'], note_text, section_name)
        else:
            notes = session.get('notes', [])
            notes.append({
                'text': note_text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'section': section_name
            })
            session['notes'] = notes
            db.save_session(session['guest_id'], json.dumps(session.get('history', [])), json.dumps(notes))
    return redirect(url_for('guest_cabinet'))


@app.route('/masterclass')
def masterclass():
    return render_template('masterclass.html')


@app.route('/quiz', methods=['POST'])
def quiz():
    questions = {
        'q1': 'гордон фримен',
        'q2': 'монтировка',
        'q3': 'хеф-костюм',
        'q4': 'вортигонт',
        'q5': 'g-man'
    }
    score = 0
    for key, correct in questions.items():
        if request.form.get(key, '').strip().lower() in correct.lower():
            score += 1

    note_text = f"Результат викторины по Half‑Life: {score} из {len(questions)} баллов"
    if 'user_id' in session:
        db.add_user_note(session['user_id'], note_text, 'quiz')
    else:
        notes = session.get('notes', [])
        notes.append({
            'text': note_text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'section': 'quiz'
        })
        session['notes'] = notes
        db.save_session(session['guest_id'], json.dumps(session.get('history', [])), json.dumps(notes))

    return render_template('masterclass.html', quiz_result=score, total=len(questions))


@app.route('/advanced_quiz', methods=['POST'])
def advanced_quiz():
    action = request.form.get('action')
    result = ""
    if action == 'simulation':
        selected = request.form.get('sim_action')
        if selected == 'evacuate_first':
            result = "Верно! При резонансном каскаде нужно немедленно покинуть зону и найти противорадиационный костюм."
        else:
            result = "Опасно тушить огонь в лаборатории – вокруг радиоактивные материалы. Сначала эвакуируйтесь."
        note_text = f"Симуляция Black Mesa: {result}"
        if 'user_id' in session:
            db.add_user_note(session['user_id'], note_text, 'simulation')
        else:
            notes = session.get('notes', [])
            notes.append(
                {'text': note_text, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'section': 'simulation'})
            session['notes'] = notes
            db.save_session(session['guest_id'], json.dumps(session.get('history', [])), json.dumps(notes))
    elif action == 'sort_gear':
        selected = request.form.get('gear_order')
        correct = "монтировка,пистолет,дробовик,арбалет"
        if selected == correct:
            result = "Идеально! Монтировка сначала, затем огнестрел."
        else:
            result = "Неправильно. Порядок выживания: монтировка, пистолет, дробовик, арбалет."
        note_text = f"Сортировка оружия: {result}"
        if 'user_id' in session:
            db.add_user_note(session['user_id'], note_text, 'sort_gear')
        else:
            notes = session.get('notes', [])
            notes.append(
                {'text': note_text, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'section': 'sort_gear'})
            session['notes'] = notes
            db.save_session(session['guest_id'], json.dumps(session.get('history', [])), json.dumps(notes))
    elif action == 'find_mistake':
        selected = request.form.get('mistake')
        if selected == 'ковер_мешает':
            result = "Верно! Ковёр на пути к эвакуации может привести к падению во время бегства от хедкрабов."
        else:
            result = "Неправильно. Настоящая ошибка — ковёр у выхода."
        note_text = f"Ошибка в плане эвакуации: {result}"
        if 'user_id' in session:
            db.add_user_note(session['user_id'], note_text, 'mistake')
        else:
            notes = session.get('notes', [])
            notes.append(
                {'text': note_text, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'section': 'mistake'})
            session['notes'] = notes
            db.save_session(session['guest_id'], json.dumps(session.get('history', [])), json.dumps(notes))
    return render_template('masterclass.html', sim_result=result)


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash('Введите поисковый запрос', 'warning')
        return redirect(url_for('index'))

    query_lower = query.lower()
    results = []
    for section_name, data in CONTENT.items():
        text = data['text']
        clean_text = re.sub(r'<[^>]+>', ' ', text).lower()
        title = data['title'].lower()
        if query_lower in clean_text or query_lower in title:
            pos = clean_text.find(query_lower)
            start = max(0, pos - 50)
            end = min(len(clean_text), pos + 100)
            snippet = clean_text[start:end] + '...'
            results.append({
                'section': section_name,
                'title': data['title'],
                'snippet': snippet
            })
    return render_template('search_results.html', query=query, results=results)


@app.route('/export_pdf')
def export_pdf():
    if 'user_id' in session:
        history_rows = db.get_user_history(session['user_id'])
        notes_rows = db.get_user_notes(session['user_id'])
        username = session['username']
    else:
        history_rows = [(item, '') for item in session.get('history', [])]
        notes_rows = [(note['text'], note.get('section', ''), note.get('timestamp', '')) for note in
                      session.get('notes', [])]
        username = 'Гость'

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 20

    c.setFont("Helvetica-Bold", 16)
    c.drawString(20, y, f"Half-Life: Black Mesa — {username}")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, y, "История просмотров:")
    y -= 15
    c.setFont("Helvetica", 10)
    for item, ts in history_rows:
        if y < 40:
            c.showPage()
            y = height - 20
        line = f"• {item}" + (f" ({ts})" if ts else "")
        c.drawString(20, y, line)
        y -= 12

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, y, "Заметки:")
    y -= 15
    c.setFont("Helvetica", 10)
    for note_text, section, ts in notes_rows:
        if y < 50:
            c.showPage()
            y = height - 20
        lines = simpleSplit(note_text, "Helvetica", 10, width - 40)
        for line in lines:
            c.drawString(20, y, line)
            y -= 10
        c.drawString(20, y, f"  — [{section}] {ts}")
        y -= 15

    c.save()
    buf.seek(0)
    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=half_life_data.pdf'
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        if not username or not email or not password:
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('register.html')
        user_id = db.create_user(username, email, password)
        if user_id:
            flash('Регистрация успешна! Войдите.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь с таким именем или email уже существует', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):
            session['user_id'] = user[0]
            session['username'] = user[1]
            if 'guest_id' in session:
                db.migrate_guest_data_to_user(user[0], session['guest_id'])
                session.pop('guest_id', None)
                session.pop('history', None)
                session.pop('notes', None)
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)