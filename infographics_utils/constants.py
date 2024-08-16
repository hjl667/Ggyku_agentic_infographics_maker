import os

QUOTE_MARK = '""'
PARAGRAPH_COUNT = 3
INFOGRAPHICS_THRESHOLD = 200

# asset paths
ASSETS_PATH = "src/news_writer/infographics_utils/assets"

REGULAR_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
BOLD_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
QUOTE_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def make_save_path(file_name: str):
    return os.path.join(ASSETS_PATH, file_name)


QUOTE_ICON_PATH = make_save_path("quote_icon.png")
QUOTE_TEXT_PATH = make_save_path("quote.png")
QUOTE_COMPONENT_PATH = make_save_path("quote_icon.png")

SUBTITLE_PATH = make_save_path("subtitle.png")

TEXT_BLOCK_01_PATH = make_save_path("text01.png")
TEXT_BLOCK_02_PATH = make_save_path("text02.png")
TEXT_BLOCK_03_PATH = make_save_path("text03.png")

SECTION_01_PATH = make_save_path("text_block_01.png")
SECTION_02_PATH = make_save_path("text_block_02.png")

TERM_BLOCK_PATH = make_save_path("term_block.png")
TERM_BLOCK_02_PATH = make_save_path("term_block_02.png")

TERM_TEXT_PATH = make_save_path("term_text.png")
EXPLANATION_PATH = make_save_path("explanation.png")
TEXT_BLOCK_TERM_PATH = make_save_path("text_block_term.png")

TERM_ILLUSTRATION_PATH = make_save_path("term_illustration.png")
TERM_ILLUSTRATION_02_PATH = make_save_path("term_illustration02.png")
HEADER_IMAGE_PATH = make_save_path("header_image.png")

GRAPH_PATH = make_save_path("graph.png")

INFOGRAPHICS_PATH = make_save_path("infographics.png")

# image specifications
IMAGE_WIDTH = 800

SPACING_01 = 30
SPACING_02 = 25
SPACING_03 = 20

ICON_RATIO = 0.8
ICON_TEXT_WIDTH = 100
ICON_TEXT_HEIGHT = 100
ICON_SIZE = 100

QUOTE_MAX_CHAR = 45
QUOTE_FONT = 23

TERM_ILLUSTRATION_WIDTH = 260
TERM_TEXT_SPACING = 100
TERM_ILLUSTRATION_SPCAING = 120
TERM_TEXT_SPACING_02 = 400
TERM_ILLUSTRATION_SPACING_02 = 90

CROP_RATIO = 0.30
PROCESSING_WIDTH_HEIGHT = 100

CLUSTER_RATIO_01 = 0.2126
CLUSTER_RATIO_02 = 0.7152
CLUSTER_RATIO_03 = 0.0722
DEFAULT_CLUSTER_NUMBER = 6
DEFUALT_COLOR_NUMBER = 10
DEFAULT_UNIFIED_COLOR_NUMBBR = 2
K_CLUSTER_NUMBER = 4

LINE_SPACING = 5
DEFAULT_FONT_SIZE = 20
SUBTITLE_RATIO = 1.4

DEFAULT_CN_MAX_CHAR = 65
DEFAULT_EN_MAX_CHAR = 50

SUBTITLE_MAX_CHAR = 45
SUBTITLE_FONT = 22

TERM_MAX_CHAR = 15
TERM_FONT = 25

EXP_MAX_CHAR = 26
EXP_FONT = 20