import os
from pathlib import Path

from PIL import Image


def extract_square(input_image_path, target_size=False, move_vertical=1, move_horizontal=1, zoom=1):
    """Crop a square region from an image with optional zoom and directional offset. Optionally resize to a target size."""
    # Load the original image
    img = Image.open(input_image_path)

    # Determine the size to create a square image
    min_dimension = min(img.width, img.height) * zoom

    # Calculate the coordinates for cropping to get the middle part
    left   = (img.width  * move_horizontal - min_dimension) // 2
    right  = (img.width  * move_horizontal + min_dimension) // 2
    top    = (img.height * move_vertical   - min_dimension) // 2
    bottom = (img.height * move_vertical   + min_dimension) // 2

    # Crop the image
    img_cropped = img.crop((left, top, right, bottom))
    if target_size:
        img_cropped = decrease_image_size(img_cropped, target_size)

    return img_cropped


def extract_image(input_image_path, target_size=False):
    """docstring."""
    # Load the original image
    img = Image.open(input_image_path)
    ratio = img.height / img.width

    if not target_size:
        return img

    # Resize the image
    img_resized = img.resize((target_size, int(target_size * ratio)), Image.Resampling.LANCZOS)

    return img_resized


def decrease_image_size(img, target_size):
    """Resize an image to a specified square dimension using high-quality resampling."""
    # if target_size >= img.width or target_size >= img.height:
    #     raise ValueError("Target size should be smaller than the original size.")

    img_resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return img_resized


def save_image_with_unique_name(img, output_folder='output', output_subfolder="", output_filename='output_image', file_type='jpg'):
    """Save an image with a unique filename and configurable file type."""
    file_type = file_type.lower().replace('.', '')
    output_filename = f"{output_filename}.{file_type}"

    output_base_path = Path() / '../' / output_folder / output_subfolder / output_filename
    output_image_path = create_unique_file_name(output_base_path)

    # --- Dispatch based on file type ---
    if file_type in ('jpg', 'jpeg'):
        return _save_as_jpg(img, output_image_path)

    elif file_type == 'png':
        return _save_as_png(img, output_image_path)

    elif file_type == 'pdf':
        return _save_as_pdf(img, output_image_path)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def _save_as_jpg(img, path):
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.save(path, "JPEG", quality=100, subsampling=0)
    return path


def _save_as_png(img, path):
    img.save(path, "PNG", compress_level=0)
    return path


def _save_as_pdf(img, path, dpi=300):
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.save(path, "PDF", resolution=float(dpi), quality=100, subsampling=0)
    return path


def create_unique_file_name(output_base_path):
    """Generate a unique file path by appending a counter if the base path already exists."""
    count = 0
    output_base_path = str(output_base_path)
    output_image_path = output_base_path
    while os.path.exists(output_image_path):
        count += 1
        output_image_path = f"{output_base_path.rsplit('.', 1)[0]}_{count}.{output_base_path.rsplit('.', 1)[1]}"
    return output_image_path
