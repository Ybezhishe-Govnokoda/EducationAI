from g4f.client import Client
from flask import Flask, jsonify
from config import OPENAI_API_KEY

app = Flask(__name__)
client = Client(api_key = OPENAI_API_KEY)

@app.route('/request', methods=['ASK'])
def ask_gpt(promt: str)->str:
    #Открытие файла со всеми лекциями
    with open("database.txt") as file:
        database = file.readlines()
    file.close()

    #Вопрос к чатГПТ на основе этого материала
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Используя эту информацию: {database} ответь на вопрос: {promt}"
            }]
        )
        return jsonify(response.choices[0].message.content)

    except Exception as err:
        return jsonify(f"An error occurred:{err}")
