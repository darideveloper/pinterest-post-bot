import numpy as np
from PIL import Image


def crop_image(image_path: str):
    """ Remove empty area from image

    Args:
        image_path (str): Path of image to crop
    """

    image = Image.open(image_path)
    a = np.array(image)[:, :, :3]  # keep RGB only
    m = np.any(a != [255, 255, 255], axis=2)
    coords = np.argwhere(m)
    y0, x0, y1, x1 = *np.min(coords, axis=0), *np.max(coords, axis=0)
    crop_data = (x0, y0, x1 + 1, y1 + 1)
    image_crop = image.crop(crop_data)
    image_crop.save(image_path)
