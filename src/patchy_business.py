import random

from PIL import Image, ImageDraw


def swap_random_patches(img, patch_fraction=0.1, n_swaps=10, seed=None):
    """Swap random non-overlapping square patches in an image."""

    if seed is not None:
        random.seed(seed)

    img = img.copy()
    size = img.width
    patch_size = int(size * patch_fraction)

    for _ in range(n_swaps):

        x1 = random.randint(0, size - patch_size)
        y1 = random.randint(0, size - patch_size)

        # Limit attempts
        for _ in range(100):
            x2 = random.randint(0, size - patch_size)
            y2 = random.randint(0, size - patch_size)

            same_position = (x1 == x2) and (y1 == y2)

            overlap = not (
                (x1 + patch_size <= x2) or
                (x2 + patch_size <= x1) or
                (y1 + patch_size <= y2) or
                (y2 + patch_size <= y1)
            )

            if not same_position and not overlap:
                break
        else:
            print("Patch fraction is too big.")
            return img

        patch1 = img.crop((x1, y1, x1 + patch_size, y1 + patch_size))
        patch2 = img.crop((x2, y2, x2 + patch_size, y2 + patch_size))

        img.paste(patch2, (x1, y1))
        img.paste(patch1, (x2, y2))

    return img


import random


def swap_random_circles(img, patch_fraction=0.1, n_swaps=10, seed=None):
    """Swap random non-overlapping circular patches in an image."""

    if seed is not None:
        random.seed(seed)

    img = img.copy()
    size = img.width
    diameter = int(size * patch_fraction)

    for _ in range(n_swaps):

        x1 = random.randint(0, size - diameter)
        y1 = random.randint(0, size - diameter)

        for _ in range(100):
            x2 = random.randint(0, size - diameter)
            y2 = random.randint(0, size - diameter)

            same_position = (x1 == x2) and (y1 == y2)

            overlap = not (
                (x1 + diameter <= x2) or
                (x2 + diameter <= x1) or
                (y1 + diameter <= y2) or
                (y2 + diameter <= y1)
            )

            if not same_position and not overlap:
                break
        else:
            continue

        patch1 = img.crop((x1, y1, x1 + diameter, y1 + diameter))
        patch2 = img.crop((x2, y2, x2 + diameter, y2 + diameter))

        mask = Image.new("L", (diameter, diameter), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, diameter, diameter), fill=255)

        img.paste(patch2, (x1, y1), mask)
        img.paste(patch1, (x2, y2), mask)

    return img
