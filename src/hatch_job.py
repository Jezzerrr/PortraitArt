import numpy as np
from PIL import Image, ImageDraw


def image_to_stripes(img, angle=45, n_candidates=8000, darkness_power=1.5, darkness_threshold=0.25, min_length=8, max_length=None, step=2, line_width=1, seed=None):
    """Convert an image into same-angle black stripes with density based on darkness."""

    if seed is not None:
        np.random.seed(seed)

    img_gray = img.convert("L")
    width, height = img_gray.size
    img_array = np.array(img_gray)

    if max_length is None:
        max_length = max(width, height)

    output = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output)

    angle_rad = np.deg2rad(angle)
    dx = np.cos(angle_rad)
    dy = np.sin(angle_rad)

    for _ in range(n_candidates):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)

        darkness = 1 - img_array[y, x] / 255

        # Darker pixels are more likely to start a line
        if np.random.random() > darkness ** darkness_power:
            continue

        x_start, y_start = grow_line(img_array, x, y, -dx, -dy, step, max_length / 2, darkness_threshold)
        x_end, y_end = grow_line(img_array, x, y, dx, dy, step, max_length / 2, darkness_threshold)

        length = np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)

        if length < min_length:
            continue

        draw.line((x_start, y_start, x_end, y_end), fill="black", width=line_width)

    return output


def grow_line(img_array, x, y, dx, dy, step, max_distance, darkness_threshold):
    """Grow a line in one direction while the image stays dark enough."""

    height, width = img_array.shape

    current_x = x
    current_y = y
    travelled = 0

    while travelled < max_distance:
        next_x = current_x + dx * step
        next_y = current_y + dy * step

        ix = int(round(next_x))
        iy = int(round(next_y))

        if ix < 0 or ix >= width or iy < 0 or iy >= height:
            break

        darkness = 1 - img_array[iy, ix] / 255

        if darkness < darkness_threshold:
            break

        current_x = next_x
        current_y = next_y
        travelled += step

    return current_x, current_y
