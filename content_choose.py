from config import OPENAI_API_KEY
from g4f.client import Client
from flask import Flask, jsonify

app = Flask(__name__)
client = Client(api_key = OPENAI_API_KEY)

#Определение начального уровня обучающегося
@app.route('/recommend', methods=['START_COURSE'])
def start_positioning(result: str, direction_of_study: str)->str:
    #Здесь в качестве result нужно передать весь текст лекции с ответами.
    #Открываем список с лекциями
    with open("lessons_list.txt") as file:
        database = file.readlines()
    file.close()

    #Рекомендация
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Зная, что студент в качестве направления обучения выбрал {direction_of_study} и результат его входного теста {result} определи уровень его подготовки и порекомендуй ему лекцию из списка: {database}. Учти, что мoжно так же порекомендовать краткое содержание этой лекции."
            }]
        )
        return jsonify(response.choices[0].message.content)

    except Exception as err:
        return jsonify(f"An error occurred:{err}")

#Рекомендации в процессе обучения
@app.route('/recommend', methods=['STUDY_IN_PROCESS'])
def choose_course(result: str)->str:
    #Здесь тоже
    with open("lessons_list.txt") as file:
        database = file.readlines()
    file.close()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Зная результат промежуточного теста {result}, подскажи, какой варинат прохождения посоветуешь?(ускоренный, с кратким содержанием лекций/обычный?"
            }]
        )
        return jsonify(response.choices[0].message.content)

    except Exception as err:
        return jsonify(f"An error occurred:{err}")
#.