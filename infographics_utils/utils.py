import json
from collections import Counter

import numpy as np
import requests
from PIL import Image
from sklearn.cluster import KMeans

from src.news_writer.infographics_utils.constants import (
    CLUSTER_RATIO_01,
    CLUSTER_RATIO_02,
    CLUSTER_RATIO_03,
    CROP_RATIO,
    DEFAULT_CLUSTER_NUMBER,
    DEFAULT_UNIFIED_COLOR_NUMBBR,
    DEFUALT_COLOR_NUMBER,
    HEADER_IMAGE_PATH,
    IMAGE_WIDTH,
    INFOGRAPHICS_THRESHOLD,
    K_CLUSTER_NUMBER,
    PROCESSING_WIDTH_HEIGHT,
    SPACING_01,
    TERM_BLOCK_02_PATH,
    TERM_BLOCK_PATH,
    TERM_ILLUSTRATION_02_PATH,
    TERM_ILLUSTRATION_PATH,
    TERM_ILLUSTRATION_SPACING_02,
    TERM_ILLUSTRATION_SPCAING,
    TERM_ILLUSTRATION_WIDTH,
    TERM_TEXT_SPACING,
    TERM_TEXT_SPACING_02,
    TEXT_BLOCK_TERM_PATH,
)
from src.news_writer.infographics_utils.make_text_block import (
    make_term_explanation_text_block,
)
from src.shared.prompts.prompt_builder import Prompt, PromptBuilder
from src.shared.types.news import ArticleProcessingTask, Language, Listen2AICategory
from src.shared.utils import log
from src.shared.utils.llm import create_message
from src.shared.utils.openai import get_image


def get_illustration_idea(term: dict):
    builder = PromptBuilder()
    TASK = f"""Generate a detailed one-sentence illustration idea to describe a static scene to visually explain a terminology. The term is {term["term"]}; one sentence explanation is {term["explanation"]}."""
    REQUIREMENTS = """- The static scene has to be clean, simple, minimal and to-the-point.
- The static scene should have no decorative surroundings and no backdrop.
- The static scene should have just one object/figure/symbol/icon.
- Generate a complete description of how the static scene should look like.
- Only output the one sentence illustration without any introduction"""
    builder.append(TASK + REQUIREMENTS)
    prompt = builder.get_final_result()
    term["illustration"] = create_message(
        prompt, "", task_type=ArticleProcessingTask.GENERATE_SCRIPT
    )
    return term


def get_term(script: dict, first_term: str = ""):
    retry_limit = 3
    attempts = 0

    while attempts < retry_limit:
        try:
            builder = PromptBuilder()
            TASK = "Extract one key professional term to explain from the news script below."
            REQUIREMENTS = f"""- Provide the extracted term and one sentence explanation.
        - The term you come up with cannot be {first_term}.
        - Ensure the final output is in valid JSON format, structured as follows:
        - The English term should be at most 3 words and the Explanation should have at most 12 words."""
            JSON_FORMAT = """{{
            "term": "<extracted_term>",
            "explanation": "<term_explanation>",
          }}
          Note: Accuracy in JSON format is crucial. Please double check to avoid any critical errors."""
            SOURCE = f"news script: {script}"
            builder.append(TASK + REQUIREMENTS + JSON_FORMAT + SOURCE)
            prompt = builder.get_final_result()

            term = create_message(prompt, "", task_type=ArticleProcessingTask.GENERATE_SCRIPT)
            return get_illustration_idea(json.loads(term))
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            attempts += 1
            log.info(f"Attempt {attempts}")
    return None


def generate_term_illustration(term: dict, is_second: bool = False):
    builder = PromptBuilder()
    STYLE = "isolated pure white background, vector artwork, flat symbols, flat vector illustration, simple and minimal, --v 5 --q 2, --s 750"
    SCENE = term["illustration"]
    builder.append(f"1({SCENE}) Styles: {STYLE}")
    image_url = get_image(builder.get_final_result())
    image_response = requests.get(image_url)

    if is_second:
        if image_response.status_code == 200:
            with open(TERM_ILLUSTRATION_02_PATH, "wb") as f:
                f.write(image_response.content)
            log.info("Image downloaded successfully.")
        else:
            log.error("Failed to download image.")
    else:
        if image_response.status_code == 200:
            with open(TERM_ILLUSTRATION_PATH, "wb") as f:
                f.write(image_response.content)
            log.info("Image downloaded successfully.")
        else:
            log.error("Failed to download image.")


def generate_term_explanation_component(text: dict, is_second: bool = False, first_term: str = ""):
    term = get_term(text, first_term)
    generate_term_illustration(term, is_second)
    colors = get_prominent_colors(image_path=TERM_ILLUSTRATION_PATH, num_colors=2)
    background_color = colors[0][0]
    if is_second:
        make_styles_match_infographics(TERM_ILLUSTRATION_02_PATH, 6)
        resize_generate_illustration(False, TERM_ILLUSTRATION_WIDTH, TERM_ILLUSTRATION_02_PATH)

    make_term_explanation_text_block(background_color, term["term"], term["explanation"], "cn")

    resize_generate_illustration(False, TERM_ILLUSTRATION_WIDTH, TERM_ILLUSTRATION_PATH)
    text_block = Image.open(TEXT_BLOCK_TERM_PATH)
    canvas = Image.new("RGB", (IMAGE_WIDTH, TERM_ILLUSTRATION_WIDTH), background_color)
    if is_second:
        term_illustration = Image.open(TERM_ILLUSTRATION_02_PATH)

        canvas.paste(text_block, (TERM_TEXT_SPACING, SPACING_01))
        canvas.paste(term_illustration, (TERM_ILLUSTRATION_SPCAING + text_block.width, 0))

        canvas.save(TERM_BLOCK_02_PATH)
        log.info("term block generated and saved as 'term_block02.png'")

    else:
        term_illustration = Image.open(TERM_ILLUSTRATION_PATH)

        canvas.paste(term_illustration, (TERM_ILLUSTRATION_SPACING_02, 0))
        canvas.paste(text_block, (TERM_TEXT_SPACING_02, SPACING_01))

        canvas.save(TERM_BLOCK_PATH)
        log.info("term block generated and saved as 'term_block.png'")

    return term["term"]


def resize_generate_illustration(is_header: bool, width, image_path):
    with Image.open(image_path) as img:
        aspect_ratio = img.height / img.width
        height = int(aspect_ratio * width)
        resized_img = img.resize((width, height), Image.LANCZOS)
        if is_header:
            crop_height = int(height * CROP_RATIO)
            resized_img = resized_img.crop((0, 0, width, crop_height))
            log.info(f"Image cropped to {width}x{crop_height}")
        resized_img.save(image_path)
        log.info(f"Image successfully resized to {width}x{height}")


def get_prominent_colors(image_path=TERM_ILLUSTRATION_PATH, num_colors=DEFUALT_COLOR_NUMBER):

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize((PROCESSING_WIDTH_HEIGHT, PROCESSING_WIDTH_HEIGHT))
        pixels = list(img.getdata())
        color_counter = Counter(pixels)
        most_common_colors = color_counter.most_common(num_colors)
        return most_common_colors


def get_color_clusters(image_path=TERM_ILLUSTRATION_PATH, num_colors=DEFAULT_CLUSTER_NUMBER):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize((PROCESSING_WIDTH_HEIGHT, PROCESSING_WIDTH_HEIGHT))
        pixels = np.array(img.getdata())

        kmeans = KMeans(n_clusters=num_colors)
        kmeans.fit(pixels)

        prominent_colors = kmeans.cluster_centers_
        prominent_colors = [tuple(map(int, color)) for color in prominent_colors]

        prominent_colors.sort(
            key=lambda color: CLUSTER_RATIO_01 * color[0]
            + CLUSTER_RATIO_02 * color[1]
            + CLUSTER_RATIO_03 * color[2]
        )

        return prominent_colors


def unify_bg_color(new_colors, img_path=HEADER_IMAGE_PATH):
    image = Image.open(img_path).convert("RGB")
    old_colors = get_prominent_colors(img_path)
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            current_color = pixels[x, y]
            if current_color == old_colors[0][0]:
                pixels[x, y] = new_colors[0][0]

    image.save(img_path)


def make_styles_match_infographics(img_path, num_clusters=DEFAULT_UNIFIED_COLOR_NUMBBR):
    replace_colors_with_clusters(img_path, num_clusters)
    colors = get_prominent_colors(image_path=TERM_ILLUSTRATION_PATH, num_colors=4)
    unify_bg_color(colors, img_path)


def replace_colors_with_clusters(image_path=HEADER_IMAGE_PATH, num_clusters=K_CLUSTER_NUMBER):
    img = Image.open(image_path)
    img = img.convert("RGB")

    data = np.array(img)
    original_shape = data.shape
    pixels = data.reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(pixels)

    new_pixels = kmeans.cluster_centers_[kmeans.labels_].astype(int)
    new_image_data = new_pixels.reshape(original_shape)

    new_img = Image.fromarray(new_image_data.astype("uint8"), "RGB")

    new_img.save(image_path)
    log.info(f"Image saved to {image_path}")


def determine_need_infographics(language: Language, topic: Listen2AICategory, score):
    if language not in [Language.ENGLISH] or topic not in [
        Listen2AICategory.BUSINESS,
        Listen2AICategory.TECHNOLOGY,
    ]:
        return False

    return score >= INFOGRAPHICS_THRESHOLD