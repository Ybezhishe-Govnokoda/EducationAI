from g4f.client import Client
from config import OPENAI_API_KEY

client = Client(api_key = OPENAI_API_KEY)

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
        return response.choices[0].message.content

    except Exception as err:
        return f"An error occurred:{err}"
