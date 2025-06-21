from flask import Flask, render_template, request, redirect, jsonify, session

from databaser import Databaser
from LLM import LlmForUser

import os
from dotenv import load_dotenv
import re


app = Flask(__name__)
db = Databaser()
llm = LlmForUser()
load_dotenv()

llm.start_chat(os.getenv('CHAT_START_PROMPT'))
app.secret_key = os.getenv('SECRET_KEY')


# Страница с авторизацией
@app.route('/', methods=['POST', 'GET'])
def authorize():
    session.clear()

    if request.method == 'POST':
        user = db.check_user(request.form['user_email'], request.form['user_password'])
        if user != 'None':
            session['user_id'] = user['user_id']
            return redirect('/main')
        else:
            return render_template('login.html')

    else:
        return render_template('login.html')


# Страница с регистрацией
@app.route('/reg', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        db.add_user(request.form['user_name'],
                    request.form['user_email'],
                    request.form['user_password'])
        return redirect('/')
    else:
        return render_template('sign_up.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# Тут будет главная с навигацией
@app.route('/main')
def main():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    courses = db.get_courses()
    course_lessons = {}

    for course in courses:
        course_lessons[course['id']] = db.get_files_from_course(course['id'])

    user = db.get_user(user_id)
    return render_template('main.html',
                           user=user,
                           courses=courses,
                           course_lessons=course_lessons)


# Добавление курса
@app.route('/add-course', methods=['POST'])
def api_add_course():
    data = request.get_json()
    course_name = data.get('course_name')

    if not course_name:
        return jsonify({'success': False, 'message': 'Нет имени курса'}), 400

    db.add_course(course_name)

    return jsonify({'success': True, 'course_name': course_name})


# Добавление файла в курс
@app.route('/add-lesson', methods=['POST'])
def add_lesson():
    course_id = request.form.get('course_id')
    lesson_name = request.form.get('lesson_name')
    lesson_file = request.files.get('lesson_file')

    mime_type = lesson_file.mimetype

    if (not mime_type.startswith('video/') and
            not mime_type.startswith('audio/') and
            not mime_type.startswith('text/')
    ):
        return 'Некорректные данные', 400

    save_dir = 'static/uploads'
    os.makedirs(save_dir, exist_ok=True)
    filename = lesson_file.filename
    filepath = os.path.join(save_dir, filename).replace('\\', '/')
    lesson_file.save(filepath)

    db.add_file_to_course(
        course_id=int(course_id),
        name=lesson_name,
        path=filepath,
        type=mime_type
    )
    return redirect('/main')


# Страница с видео-уроком и чатом
@app.route('/<video>')
def video_page(video):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    user = db.get_user(user_id)
    # ОБЯЗАТЕЛЬНО СМЕНИ test на video_page
    return render_template('test.html', user=user, video=video)

# Вспомогательная для чата
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'reply': 'Пустое сообщение'}), 400

    try:
        reply = llm.add_message(user_message)
        reply = str(reply)

        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()

        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Ошибка LLM: {str(e)}'}), 500



# Чисто для тестов жи есть
@app.route('/test', methods=['POST', 'GET'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True)