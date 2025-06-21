from flask import Flask, render_template, request, redirect, jsonify

from databaser import Databaser
from LLM import LlmForUser
from config import CHAT_START_PROMPT

from urllib.parse import unquote
import re


app = Flask(__name__)
db = Databaser()
llm = LlmForUser()

llm.start_chat(CHAT_START_PROMPT)
name = ''


# Страница с авторизацией
@app.route('/', methods=['POST', 'GET'])
def authorize():
    if request.method == 'POST':
        user = db.check_user(request.form['user_email'], request.form['user_password'])
        if user != 'None':
            global name
            name = user[1]
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


# Тут будет главная с навигацией
@app.route('/main')
def main():
    courses = db.get_courses()
    course_lessons = {}

    for course in courses:
        course_lessons[course['id']] = db.get_files_from_course(course['id'])

    return render_template('main.html',
                           name=name,
                           courses=courses,
                           course_lessons=course_lessons)


# Добавление курса
@app.route('/api/add-course', methods=['POST'])
def api_add_course():
    data = request.get_json()
    course_name = data.get('course_name')

    if not course_name:
        return jsonify({'success': False, 'message': 'Нет имени курса'}), 400

    db.add_course(course_name)

    return jsonify({'success': True, 'course_name': course_name})


# Страница с видео-уроком и чатом
@app.route('/<video>')
def video_page(video):
    # ОБЯЗАТЕЛЬНО СМЕНИ test на video_page
    return render_template('test.html', name=name, video=video)

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