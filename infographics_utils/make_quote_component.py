from PIL import Image, ImageDraw, ImageFont

from infographics_utils.constants import (
    BOLD_FONT_PATH,
    ICON_RATIO,
    ICON_SIZE,
    ICON_TEXT_HEIGHT,
    ICON_TEXT_WIDTH,
    IMAGE_WIDTH,
    QUOTE_COMPONENT_PATH,
    QUOTE_FONT,
    QUOTE_FONT_PATH,
    QUOTE_ICON_PATH,
    QUOTE_MARK,
    QUOTE_MAX_CHAR,
    QUOTE_TEXT_PATH,
    SPACING_01,
    SPACING_02,
    SPACING_03,
)
from src.news_writer.infographics_utils.make_text_block import wrap_text_to_image
from src.shared.prompts.prompt_builder import PromptBuilder
from src.shared.types.news import ArticleProcessingTask
from src.shared.utils.llm import create_message


def create_quote_icon(icon_size, icon_color, bg_color):
    icon = Image.new("RGB", (icon_size, icon_size), bg_color)
    draw = ImageDraw.Draw(icon)

    font_path = QUOTE_FONT_PATH
    font = ImageFont.truetype(font_path, int(icon_size * ICON_RATIO))

    quote_mark = QUOTE_MARK
    text_width = ICON_TEXT_WIDTH
    text_height = ICON_TEXT_HEIGHT
    text_x = (icon_size - text_width) / 2
    text_y = (icon_size - text_height) / 2

    draw.text((text_x, text_y), quote_mark, font=font, fill=icon_color)
    icon.save(QUOTE_ICON_PATH)


def create_quote_component(quote, bg_color, quote_icon_color):
    create_quote_icon(ICON_SIZE, quote_icon_color, bg_color)

    quote_icon = Image.open(QUOTE_ICON_PATH)
    wrap_text_to_image(bg_color, "quote", quote, QUOTE_MAX_CHAR, QUOTE_FONT, BOLD_FONT_PATH)
    quote_text = Image.open(QUOTE_TEXT_PATH)

    height = max(quote_icon.height + quote_text.height + SPACING_01, 0)
    width = IMAGE_WIDTH

    canvas = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(canvas)

    canvas.paste(quote_icon, (quote_icon.height, SPACING_03))
    canvas.paste(quote_text, (quote_icon.height + SPACING_02, quote_icon.height))
    canvas.save(QUOTE_COMPONENT_PATH)


def get_quote(script: dict):
    builder = PromptBuilder()
    TASK = "Generate one short sentence that captures the most important facts from the provided script below. Directly output the sentence without any introduction."
    SOURCE = f"script: {script}"
    builder.append(TASK + SOURCE)
    prompt = builder.get_final_result()

    return create_message(prompt, "", task_type=ArticleProcessingTask.GENERATE_SCRIPT)


def make_quote_block(script: dict, colors, color_clusters):
    quote_sentence = get_quote(script)
    create_quote_component(quote_sentence, colors[0][0], color_clusters[1])