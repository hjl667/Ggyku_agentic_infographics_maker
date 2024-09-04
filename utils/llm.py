from dotenv import load_dotenv
import os
from openai import OpenAI


load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')
MODEL = os.getenv('MODEL')


def get_llm_response(
    prompt: str,
    background,
    model=MODEL,
    **kwargs,
):
    messages = []
    client = OpenAI(
        api_key=OPENAI_KEY,
        max_retries=2,
    )
    if background:
        messages.append({"role": "system", "content": background})

    text_messages = [{"type": "text", "text": prompt}]

    messages.append(
        {
            "role": "user",
            "content": text_messages,
        }
    )
    params = {
        "messages": messages,
        "model": model,
    }
    if "response_format" in kwargs:
        params["response_format"] = kwargs["response_format"]

    chat_completion = client.chat.completions.create(**params)

    return chat_completion.choices[0].message.content


def get_image(task_description: str):
    client = OpenAI(
        api_key=OPENAI_KEY,
        max_retries=2,
    )
    response = client.images.generate(
        model="dall-e-3",
        prompt=task_description,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url