import json
import textwrap

from PIL import Image, ImageDraw, ImageFont

from infographics_utils.constants import (
    BOLD_FONT_PATH,
    DEFAULT_CN_MAX_CHAR,
    DEFAULT_EN_MAX_CHAR,
    DEFAULT_FONT_SIZE,
    EXP_FONT,
    EXP_MAX_CHAR,
    EXPLANATION_PATH,
    IMAGE_WIDTH,
    LINE_SPACING,
    PARAGRAPH_COUNT,
    QUOTE_COMPONENT_PATH,
    REGULAR_FONT_PATH,
    SPACING_03,
    SUBTITLE_FONT,
    SUBTITLE_MAX_CHAR,
    SUBTITLE_PATH,
    SUBTITLE_RATIO,
    TERM_BLOCK_02_PATH,
    TERM_BLOCK_PATH,
    TERM_FONT,
    TERM_MAX_CHAR,
    TERM_TEXT_PATH,
    TEXT_BLOCK_01_PATH,
    TEXT_BLOCK_02_PATH,
    TEXT_BLOCK_03_PATH,
    TEXT_BLOCK_TERM_PATH,
    make_save_path,
)
from src.news_writer.utils import format_language_display
from src.shared.prompts.prompt_builder import PromptBuilder
from src.shared.prompts.prompt_library import POLITICAL_ORIENTATION_PROMPT
from src.shared.types.news import ArticleProcessingTask, Language, PoliticalOrientation
from src.shared.utils import log
from src.shared.utils.anthropic import create_message


def wrap_text(text, max_chars, language="cn"):
    if language == "cn":
        sentence_marker = "。"
    else:
        sentence_marker = "."
    sentences = text.split(sentence_marker)
    paragraphs = []
    for i in range(0, len(sentences), 2):
        paragraph = sentence_marker.join(sentences[i : i + 2])
        wrapped_paragraph = textwrap.fill(paragraph, max_chars)
        paragraphs.append(wrapped_paragraph)
    return "\n\n".join(paragraphs)


def wrap_text_to_image(
    bg_color,
    text_type,
    input_text,
    max_chars_per_line,
    font_size=DEFAULT_FONT_SIZE,
    font_path=REGULAR_FONT_PATH,
):
    wrapped_text = wrap_text(input_text, max_chars_per_line)

    font = ImageFont.truetype(font_path, font_size)
    lines = wrapped_text.split("\n")

    max_line_width = max(font.getbbox(line)[2] for line in lines)
    line_height = font.getbbox(lines[0])[3] - font.getbbox(lines[0])[1]
    line_spacing = LINE_SPACING
    paragraph_spacing = SPACING_03
    img_height = (
        sum(line_height + (paragraph_spacing if line == "" else line_spacing) for line in lines)
        + 2 * LINE_SPACING
    )
    img_width = max_line_width + SPACING_03

    image = Image.new("RGB", (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(image)

    y_text = LINE_SPACING

    for line in lines:
        draw.text((2 * LINE_SPACING, y_text), line, font=font, fill="black")
        y_text += line_height + line_spacing
    image_path = make_save_path(f"{text_type}.png")
    image.save(image_path)


def make_formatted_subtitle(bg_color, icon_color):
    subtitle = Image.open(SUBTITLE_PATH)
    height = int(subtitle.size[1] * SUBTITLE_RATIO)
    icon_height = SPACING_03
    width = subtitle.size[0] + 2 * icon_height
    canvas = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(canvas)
    square_icon = Image.new("RGB", (icon_height, icon_height), icon_color)
    canvas.paste(subtitle, (2 * icon_height, 0))
    canvas.paste(square_icon, (int(icon_height / 2), int(icon_height)))
    canvas.save(SUBTITLE_PATH)


def make_text_block(bg_color, icon_color, tag, subtitle, text, language="cn"):
    if language == "cn":
        max_chars_per_line = DEFAULT_CN_MAX_CHAR
    else:
        max_chars_per_line = DEFAULT_EN_MAX_CHAR
    spacing = SPACING_03
    wrap_text_to_image(
        bg_color,
        "subtitle",
        subtitle,
        SUBTITLE_MAX_CHAR,
        SUBTITLE_FONT,
        font_path=BOLD_FONT_PATH,
    )
    make_formatted_subtitle(bg_color, icon_color)
    subtitle = Image.open(SUBTITLE_PATH)

    if tag == "01":
        text01 = text[0]
        text02 = text[1]
        wrap_text_to_image(bg_color, "text01", text01, max_chars_per_line, SPACING_03)
        wrap_text_to_image(bg_color, "text02", text02, max_chars_per_line, SPACING_03)

        text_block_01 = Image.open(TEXT_BLOCK_01_PATH)
        text_block_02 = Image.open(TEXT_BLOCK_02_PATH)
        term_block = Image.open(TERM_BLOCK_PATH)

        width = IMAGE_WIDTH
        height = (
            text_block_01.size[1]
            + text_block_02.size[1]
            + subtitle.size[1]
            + term_block.size[1]
            + 5 * spacing
        )
        canvas = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(canvas)
        offset = (IMAGE_WIDTH - text_block_01.width) // 2
        canvas.paste(subtitle, (offset, 0))
        canvas.paste(text_block_01, (offset, subtitle.size[1]))
        canvas.paste(term_block, (0, subtitle.size[1] + text_block_01.size[1] + spacing))
        canvas.paste(
            text_block_02,
            (
                offset,
                subtitle.size[1] + text_block_01.size[1] + term_block.size[1] + int(3.5 * spacing),
            ),
        )
        image_path = make_save_path(f"text_block_{tag}.png")
        canvas.save(image_path)

    elif tag == "02":
        text01 = text[0]
        text02 = text[1]
        text03 = text[2]
        wrap_text_to_image(bg_color, "text01", text01, max_chars_per_line, 20)
        wrap_text_to_image(bg_color, "text02", text02, max_chars_per_line, 20)
        wrap_text_to_image(bg_color, "text03", text03, max_chars_per_line, 20)

        text_block_01 = Image.open(TEXT_BLOCK_01_PATH)
        text_block_02 = Image.open(TEXT_BLOCK_02_PATH)
        text_block_03 = Image.open(TEXT_BLOCK_03_PATH)
        term_block02 = Image.open(TERM_BLOCK_02_PATH)
        quote_block = Image.open(QUOTE_COMPONENT_PATH)
        width = IMAGE_WIDTH
        height = (
            text_block_01.size[1]
            + text_block_02.size[1]
            + text_block_03.size[1]
            + subtitle.size[1]
            + quote_block.size[1]
            + term_block02.size[1]
            + 5 * spacing
        )
        canvas = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(canvas)
        offset = (IMAGE_WIDTH - text_block_01.width) // 2

        canvas.paste(subtitle, (offset, 0))
        canvas.paste(text_block_01, (offset, subtitle.size[1]))
        canvas.paste(
            term_block02,
            (0, subtitle.size[1] + text_block_01.size[1] + spacing + int(0.5 * spacing)),
        )
        canvas.paste(
            text_block_02,
            (
                offset,
                subtitle.size[1]
                + 2 * spacing
                + text_block_01.size[1]
                + term_block02.size[1]
                + spacing,
            ),
        )
        canvas.paste(
            quote_block,
            (
                0,
                subtitle.size[1]
                + 3 * spacing
                + text_block_01.size[1]
                + term_block02.size[1]
                + text_block_02.size[1]
                + int(1.5 * spacing),
            ),
        )
        canvas.paste(
            text_block_03,
            (
                offset,
                subtitle.size[1]
                + 3 * spacing
                + text_block_01.size[1]
                + term_block02.size[1]
                + text_block_02.size[1]
                + quote_block.size[1]
                + 2 * spacing,
            ),
        )
        image_path = make_save_path(f"text_block_{tag}.png")
        canvas.save(image_path)


def make_term_explanation_text_block(bg_color, term, explanation, language="cn"):
    spacing = 20
    all_caps_term = term.upper()
    wrap_text_to_image(
        bg_color,
        "term_text",
        all_caps_term,
        TERM_MAX_CHAR,
        TERM_FONT,
        font_path=BOLD_FONT_PATH,
    )
    term = Image.open(TERM_TEXT_PATH)
    wrap_text_to_image(bg_color, "explanation", explanation, EXP_MAX_CHAR, EXP_FONT)
    explanation = Image.open(EXPLANATION_PATH)
    width = max(explanation.width, term.width)
    height = explanation.size[1] + spacing + term.size[1]
    canvas = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(canvas)

    canvas.paste(term, (0, 0))
    canvas.paste(explanation, (0, term.size[1] + spacing))
    canvas.save(TEXT_BLOCK_TERM_PATH)


def generate_text_from_news(
    news: dict,
    language: Language,
    political_orientation: PoliticalOrientation,
    section_count: int = 2,
):
    political_prompt = POLITICAL_ORIENTATION_PROMPT[political_orientation.name]
    response_language = format_language_display(language)
    SYSTEM_PROMPT = f"""{political_prompt} You must write in as much detail as possible. You're a best-seller writer in {response_language}. Respond in {response_language}. """
    retry_limit = 3
    attempts = 0

    while attempts < retry_limit:
        try:
            response = create_message(
                create_prompt_for_text_generation(news, section_count),
                SYSTEM_PROMPT,
                task_type=ArticleProcessingTask.GENERATE_SCRIPT,
                response_format={"type": "json_object"},
            )
            return validate_text_json(json.loads(response))
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            attempts += 1
            log.info(f"Attempt {attempts}")


def create_prompt_for_text_generation(news: dict, section_count: int):
    builder = PromptBuilder()
    TASK = f"""rewrite "{news["content"]}" into {section_count} sections"""
    INSTRUCTIONS = f"""(1) Craft witty, eye-catching subtitles that encapsulate each section. (2) generate a list of {PARAGRAPH_COUNT} paragraphs for each section under "content".
    (3) output the result strictly in the json format below."""
    JSON_FORMAT = """{{
            "01": {{
                "subtitle": "",
                "content": []
            }},
            "02": {{
                "subtitle": "",
                "content": []
            }}
            }} Note: Accuracy in JSON format is crucial. When entering values, remember to escape any JSON special characters (like quotes, backslashes, etc.) to prevent syntax errors. Double-check the JSON output to avoid any critical errors."""
    builder.append(TASK + INSTRUCTIONS + JSON_FORMAT)
    return builder.get_final_result()


def validate_text_json(text: dict):
    if "01" not in text or "02" not in text:
        raise ValueError("Invalid JSON format. Missing section 01 or section 02.")

    for section in ["01", "02"]:
        if "subtitle" not in text[section] or "content" not in text[section]:
            raise ValueError(
                f"Invalid JSON format. Missing subtitle or content in section {section}."
            )
        if not isinstance(text[section]["content"], list):
            raise ValueError(
                f"Invalid JSON format. The content in section {section} is not a list."
            )
        if len(text[section]["content"]) < 3:
            raise ValueError(
                f"Invalid JSON format. The content list in section {section} does not contain at least 3 elements."
            )
    log.info(text)
    return text