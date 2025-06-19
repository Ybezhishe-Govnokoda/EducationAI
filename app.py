from flask import Flask, render_template, request, redirect, jsonify
from databaser import Databaser
from LLM import LlmForUser
import re


app = Flask(__name__)
db = Databaser()
llm = LlmForUser()
llm.start_chat('Ты бот-помощник в обучении. Обязательно давай ответы только на русском языке. Иногда можно использовать английский, но только при необходимости. Если в ответе будет хоть одно китайское слово, то русские студенты уйдут от нас и моя жизнь будет разрушена')

name = ''


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


@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/video-page')
def video_page():
    # ОБЯЗАТЕЛЬНО СМЕНИ test на video_page
    return render_template('test.html', name=name)


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



@app.route('/reg', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        db.add_user(request.form['user_name'],
                    request.form['user_email'],
                    request.form['user_password'])
        return redirect('/')
    else:
        return render_template('sign_up.html')


@app.route('/test', methods=['POST', 'GET'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True)