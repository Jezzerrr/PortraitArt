import numpy as np
from PIL import Image, ImageDraw


def image_to_parallel_lines(img, angle=45, line_spacing=8, darkness_threshold=0.35, sample_step=2, min_segment_length=8, line_width=1, draw_markers=False, marker_size=4, guide_color=(225, 225, 225)):
    """
    Convert image to evenly spaced parallel line segments.
    Dark parts of the image determine where lines are visible.
    If draw_markers=True, draw soft guidelines and only mark segment start/end.

        Steps:
    1. Start with image
    2. Convert to grayscale
    3. Create many parallel guidelines
    4. Walk along every guideline
    5. Check darkness at each sample point
    6. Keep dark-enough samples
    7. Group consecutive visible samples
    8. Draw each group as a line segment
    """
    img_gray = img.convert("L")
    width, height = img_gray.size
    img_array = np.array(img_gray)

    output = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output)

    angle_rad = np.deg2rad(angle)
    dx = np.cos(angle_rad)  # Direction of the parallel lines
    dy = np.sin(angle_rad)
    nx = -np.sin(angle_rad)  # Perpendicular direction; used to place neighbouring lines
    ny = np.cos(angle_rad)

    diagonal = int(np.ceil(np.sqrt(width**2 + height**2)))
    cx = width / 2
    cy = height / 2

    offsets = np.arange(-diagonal, diagonal + line_spacing, line_spacing)

    for offset in offsets:
        base_x = cx + offset * nx
        base_y = cy + offset * ny

        if draw_markers:
            draw_guideline(draw, base_x, base_y, dx, dy, diagonal, guide_color)

        current_segment = []

        for t in np.arange(-diagonal, diagonal + sample_step, sample_step):
            x = base_x + t * dx
            y = base_y + t * dy

            ix = int(round(x))
            iy = int(round(y))

            inside_image = 0 <= ix < width and 0 <= iy < height

            if inside_image:
                darkness = 1 - img_array[iy, ix] / 255
                visible = darkness >= darkness_threshold
            else:
                visible = False

            if visible:
                current_segment.append((x, y))
            else:
                draw_segment_if_long_enough(draw, current_segment, min_segment_length, line_width, draw_markers, marker_size)
                current_segment = []

        draw_segment_if_long_enough(draw, current_segment, min_segment_length, line_width, draw_markers, marker_size)

    return output


def draw_guideline(draw, base_x, base_y, dx, dy, diagonal, guide_color):
    x1 = base_x - diagonal * dx
    y1 = base_y - diagonal * dy
    x2 = base_x + diagonal * dx
    y2 = base_y + diagonal * dy

    draw.line((x1, y1, x2, y2), fill=guide_color, width=1)


def draw_segment_if_long_enough(draw, segment, min_segment_length, line_width, draw_markers, marker_size):
    if len(segment) < 2:
        return

    x1, y1 = segment[0]
    x2, y2 = segment[-1]

    length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    if length < min_segment_length:
        return

    if draw_markers:
        draw_start_marker(draw, x1, y1, marker_size)
        draw_end_marker(draw, x2, y2, marker_size)
    else:
        draw.line((x1, y1, x2, y2), fill="black", width=line_width)


def draw_start_marker(draw, x, y, marker_size):
    r = marker_size
    draw.ellipse((x - r, y - r, x + r, y + r), outline="black", width=1)


def draw_end_marker(draw, x, y, marker_size):
    r = marker_size
    draw.line((x - r, y - r, x + r, y + r), fill="black", width=1)
    draw.line((x - r, y + r, x + r, y - r), fill="black", width=1)
