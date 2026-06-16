import random
from PIL import Image, ImageDraw


def rotate_random_circle(img, patch_fraction=0.1, angle=90, center_fraction=None, seed=None):
    """
    Rotate a random circular region in-place.

    Parameters
    ----------
    img : PIL.Image.Image
        Input image (must be square).
    patch_fraction : float
        Size of circle diameter as fraction of image size.
    angle : float
        Rotation angle in degrees.
    center_fraction : tuple or None
        Optional (x_fraction, y_fraction) for the circle centre.
        Example: (0.5, 0.5) is the middle.
        If None, a random circle is used.
    seed : int or None
        Optional random seed.

    Returns
    -------
    PIL.Image.Image
    """

    if seed is not None:
        random.seed(seed)

    img = img.copy()
    size = img.width
    diameter = int(size * patch_fraction)
    radius = diameter // 2

    if center_fraction is None:
        # Random position
        x = random.randint(0, size - diameter)
        y = random.randint(0, size - diameter)
    else:
        center_x = int(size * center_fraction[0])
        center_y = int(size * center_fraction[1])

        x = center_x - radius
        y = center_y - radius

        # Keep the full circle inside the image
        x = max(0, min(x, size - diameter))
        y = max(0, min(y, size - diameter))

    # Extract patch
    patch = img.crop((x, y, x + diameter, y + diameter))

    # Rotate patch
    # patch_rotated = patch.rotate(angle)
    patch_rotated = patch.rotate(angle, resample=Image.Resampling.BICUBIC)

    # Create circular mask
    mask = Image.new("L", (diameter, diameter), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter, diameter), fill=255)

    # Paste rotated patch back using mask
    img.paste(patch_rotated, (x, y), mask)

    return img
