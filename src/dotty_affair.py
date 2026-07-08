import numpy as np
from PIL import Image, ImageDraw


def image_to_dots(img, grid_size=10, min_radius=0, max_radius=None, jitter=None, color=True, fill=True, outline_width=1):
    """Convert an image into a field of black dots (halftone style). Inspiration: https://ohmydotz.nl/"""
    # Define max_radius
    if not max_radius:
        max_radius = grid_size / 2

    # Convert to grayscale
    img_gray = img.convert("L")

    width, height = img_gray.size
    n_cols = round(width / grid_size)
    n_rows = round(height / grid_size)

    x_edges = np.linspace(0, width, n_cols + 1, dtype=int)
    y_edges = np.linspace(0, height, n_rows + 1, dtype=int)

    # Create white canvas
    output = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output)

    # Convert to numpy for easy brightness access
    img_array = np.array(img_gray)

    for i in range(n_rows):
        for j in range(n_cols):
            # Extract grid cell
            x0, x1 = x_edges[j], x_edges[j+1]
            y0, y1 = y_edges[i], y_edges[i+1]

            if x1 <= x0 or y1 <= y0: continue

            cx = (x0 + x1) // 2
            cy = (y0 + y1) // 2

            cell_size = min(x1 - x0, y1 - y0)
            cx, cy = apply_circular_jitter(cx, cy, cell_size, jitter)

            # Clamp ONLY for sampling, NOT for drawing
            sx = max(0, min(width - 1, cx))
            sy = max(0, min(height - 1, cy))

            # Get dot size
            radius = get_radius(img_array, sx, sy, max_radius, min_radius)
            if radius is None: continue

            # Draw dot
            if fill:
                fill_color = img.getpixel((sx, sy)) if color else "black"
                draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill_color)
                draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline="grey", width=outline_width)
            else:
                draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline="grey", width=outline_width)
                # draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(120, 120, 120), width=outline_width)

    return output


def image_to_density_dots(
    img,
    grid_size=10,
    dot_radius=3,
    jitter=None,
    fill=False,
    seed=None,
):
    """Convert image to constant-size dots, with density based on brightness."""
    if seed is not None:
        np.random.seed(seed)

    img_gray = img.convert("L")
    width, height = img_gray.size

    n_cols = round(width / grid_size)
    n_rows = round(height / grid_size)

    x_edges = np.linspace(0, width, n_cols + 1, dtype=int)
    y_edges = np.linspace(0, height, n_rows + 1, dtype=int)

    output = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output)

    img_array = np.array(img_gray)

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

            # 0 = white area -> low chance
            # 1 = dark area  -> high chance
            dot_probability = 1 - brightness / 255

            if np.random.random() > dot_probability:
                continue

            bbox = (
                cx - dot_radius,
                cy - dot_radius,
                cx + dot_radius,
                cy + dot_radius,
            )

            if fill:
                draw.ellipse(bbox, fill="black")
            else:
                draw.ellipse(bbox, outline="black", width=1)

    return output


def apply_circular_jitter(cx, cy, cell_size, jitter):
    """Apply circular jitter to a point."""
    if not jitter:
        return cx, cy

    max_r = cell_size * jitter

    angle = np.random.uniform(0, 2 * np.pi)
    r = max_r * np.sqrt(np.random.uniform(0, 1))

    cx += int(r * np.cos(angle))
    cy += int(r * np.sin(angle))

    return cx, cy


def get_radius(img_array, sx, sy, max_radius, min_radius):
    brightness = img_array[sy, sx]
    radius = max_radius * (1 - brightness / 255)

    if radius < min_radius:
        return None

    return radius
