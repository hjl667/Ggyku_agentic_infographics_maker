from rembg import remove
from PIL import Image, ImageOps
import io

def remove_background(input_path, output_path, background_color=(248, 248, 255)):
    # Open the image file
    with open(input_path, 'rb') as input_file:
        input_data = input_file.read()

    # Remove the background
    output_data = remove(input_data)

    # Load the image with background removed
    img = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # Create a new background image with the ghostwhite color
    new_background = Image.new("RGBA", img.size, background_color + (255,))  # Add alpha channel with full opacity

    # Composite the original image onto the new ghostwhite background
    img_with_new_bg = Image.alpha_composite(new_background, img)

    # Save the result with the ghostwhite background
    img_with_new_bg.convert("RGB").save(output_path, "PNG")