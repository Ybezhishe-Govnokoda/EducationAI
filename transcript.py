import whisper
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/transcription', methods=['T_CREATE'])
def transcribe(path: str):
    global path_to_file
    path_to_file = path

    try:
        model = whisper.load_model("turbo")
        result = model.transcribe(path, fp16=False)

        #добавление транскрипции к общей базы данных для ответов на вопросы
        with open("database.txt", "a") as file:
            file.write(result["text"])
        file.close()

        #создание файла с текстом только этой лекции для создание краткого содержания
        with open(f"text: {path}.txt", "w") as comp_sourse:
            comp_sourse.write(result["text"])
        comp_sourse.close()

        #определение списка с файлами, для которых нужно составить кр. содерж.
        with open("source_list.txt", "a") as list:
            list.write(f"text: {path}.txt\n")
        list.close()

    except Exception as err:
        return err

#Добавление к лекции её названия и краткого описания в отдельный файл для системы рекомендаций
@app.route('/lesson_name', methods=['CHOOSE'])
def lesson_name_choosing():
    try:
        with open(f"text: {path}.txt", "r") as file:
            lesson_text = file.readlines()
        file.close()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Используя этот текст лекции: {lesson_text} название и добавь краткое описание этой лекции"
            }]
        )

        with open("lessons_list.txt", "a") as l_list:
            l_list.write(response.choices[0].message.content)

    except Exception as err:
        l_list.write(err)
        l_list.close()
#.