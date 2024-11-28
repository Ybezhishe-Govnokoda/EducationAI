from config import OPENAI_API_KEY
from g4f.client import Client
from flask import Flask, jsonify

app = Flask(__name__)
client = Client(api_key = OPENAI_API_KEY)

with open("source_list.txt") as s_list:
    need_to_compress = s_list.readlines()
s_list.close()

#замена содержимого файла его кратким содержанием
@app.route('/summary', methods=['CREATE'])
def summary_create():
    for path in need_to_compress:
        with open(path) as file:
            lesson = file.readlines()
        file.close()

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Кратко перескажи эту информацию: {lesson}"
                }]
            )
            summary = response.choices[0].message.content

        except Exception as err:
            summary = "Fail to compress"

        with open(path, "w") as response:
            response.write(jsonify(summary))
        response.close()

        # удаление из списка путей к обработанным файлам
        need_to_compress.remove(path)

    #перезапись файла обновленным списком
    with open("source_list.txt", "w") as s_list:
        s_list.write(jsonify(""))
    s_list.close()
