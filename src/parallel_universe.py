import numpy as np
from PIL import Image, ImageDraw


def image_to_grid_stripes(img, grid_size=10, angle=45, min_length=0, max_length=None, jitter=None, color=False):
    """Convert image into stripes."""
    if max_length is None:
        max_length = grid_size

    img_gray = img.convert("L")

    width, height = img_gray.size

    n_cols = round(width / grid_size)
    n_rows = round(height / grid_size)

    x_edges = np.linspace(0, width, n_cols + 1, dtype=int)
    y_edges = np.linspace(0, height, n_rows + 1, dtype=int)

    output = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output)

    img_array = np.array(img_gray)

    angle_rad = np.deg2rad(angle)

    dx_unit = np.cos(angle_rad)
    dy_unit = np.sin(angle_rad)

    for i in range(n_rows):
        for j in range(n_cols):

            x0, x1 = x_edges[j], x_edges[j + 1]
            y0, y1 = y_edges[i], y_edges[i + 1]

            if x1 <= x0 or y1 <= y0:
                continue

            cx = (x0 + x1) // 2
            cy = (y0 + y1) // 2

            cell_size = min(x1 - x0, y1 - y0)
            cx, cy = apply_circular_jitter(cx, cy, cell_size, jitter)

            sx = max(0, min(width - 1, cx))
            sy = max(0, min(height - 1, cy))

            brightness = img_array[sy, sx]

            length = max_length * (1 - brightness / 255)

            if length < min_length:
                continue

            dx = dx_unit * length / 2
            dy = dy_unit * length / 2

            if color:
                line_color = img.getpixel((sx, sy))
            else:
                line_color = "black"

            draw.line(
                (
                    cx - dx,
                    cy - dy,
                    cx + dx,
                    cy + dy,
                ),
                fill=line_color,
                width=1
            )

    return output


def apply_circular_jitter(cx, cy, cell_size, jitter):
    if not jitter:
        return cx, cy

    max_r = cell_size * jitter

    angle = np.random.uniform(0, 2 * np.pi)
    r = max_r * np.sqrt(np.random.uniform(0, 1))

    cx += int(r * np.cos(angle))
    cy += int(r * np.sin(angle))

    return cx, cy