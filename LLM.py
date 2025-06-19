import lmstudio as lms
from pathlib import Path

from bottle import response


class LlmForUser:
    def __init__(self, context_length: int = 16384, gpu_offload: float = 0.8):
        self.__chat = None
        self.__model = lms.llm("deepseek-r1-distill-llama-8b", config={
            "contextLength": context_length,
            "gpuOffload": gpu_offload,
        })

    def quick_msg(self, prompt: str):
        return self.__model.respond(prompt)

    def start_chat(self, start_prompt: str):
        try:
            self.__chat = lms.Chat(start_prompt)
        except Exception as err:
            return f"Error occurred: {err!r}"

    def add_message(self, message: str):
        try:
            self.__chat.add_user_message(message)
            reply = self.__model.respond(self.__chat)
            self.__chat.add_assistant_response(reply)
            return reply

        except Exception as err:
            return f"Error occurred: {err!r}"

    def add_msg_with_image(self, message: str, img_url: str):
        try:
            image_path = img_url
            image_handle = lms.prepare_image(image_path)
            self.__chat.add_user_message(message, images=[image_handle])
            reply = self.__model.respond(self.__chat)
            return reply

        except Exception as err:
            return f"Error occurred: {err!r}"


class LlmForSystem:
    def __init__(self, context_length: int = 16384, gpu_offload: float = 0.8):
        self.__model = lms.llm("deepseek-r1-distill-llama-8b", config={
            "contextLength": context_length,
            "gpuOffload": gpu_offload,
        })

    def dump_content(self, path: str):
        with open(path) as input_file:
            lesson = input_file.readlines()
        input_file.close()

        try:
            summary = self.__model.respond(f"Кратко перескажи этот материал: {lesson}")

            with open(f"{Path(path).stem}_dumped.json", "w",
                      encoding="utf-8") as output_file:
                output_file.write(str(summary))

        except Exception as err:
            return f"Error occurred: {err!r}"

# llm = LlmForUser()
# llm.start_chat('Представь себя в роли преподавателя, который отвечает на вопросы детей. Тебе нужно давать краткие ответы на русском языке. ОЧЕНЬ ВАЖНО СЛЕДИТЬ, ЧТОБЫ В ОТВЕТАХ БЫЛ ТОЛЬКО РУССКИЙ ЯЗЫК')
# msg = input()
# reply = llm.add_message(msg)
# print(type(reply))
# print(str(reply))
