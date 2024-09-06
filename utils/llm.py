from typing import Optional, List

from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import requests


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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def review_image(prompt, url, image_urls: Optional[List[str]] = None, model=MODEL):

    messages = []
    client = OpenAI(
        api_key=OPENAI_KEY,
        max_retries=2,
    )

    text_messages = [{"type": "text", "text": prompt}]
    image_messages = [
        {"type": "image_url", "image_url": {"url": image_url}} for image_url in (image_urls or [])
    ]

    messages.append(
        {
            "role": "user",
            "content": text_messages + image_messages,
        }
    )
    params = {
        "messages": messages,
        "model": model,
    }

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


if __name__ == "__main__":
    style = """Styles: Generate a simple 3D-like vector illustration with just one central, solid object. 
    The background should be completely blank and pure white. The object should be clean, minimalistic, 
    and clearly focused in the center of the image, with no distractions or additional elements around it. 
    Ensure the design is easy to extract or isolate from the background.
    """
    color = "colorful and appealing"
    theme = "<object>a bag of potato with an absurd price tag<object>"

    url = get_image(style+theme+color)
    print(url)

    # image_review = review_image("check if the image has just one central focused object and if the background is easy to remove", ["https://storage.googleapis.com/koduck/Screenshot%20from%202024-08-29%2013-31-27.png"])
    # print(image_review)