import os
import requests
import secrets
import numpy as np
from PIL import Image
from time import sleep

current_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(current_folder)
imgs_folder = os.path.join(parent_folder, 'static', 'imgs', 'temp')


def download_image(link: str) -> str:
    """ Download image and save in "media" folder

    Args:
        link (str): url of image

    Returns:
        str: path of image saved
    """
    
    # Get image
    res = requests.get(link)
    
    # Validate image response
    if res.status_code != 200:
        return ""
    
    # Save image
    image_hash = secrets.token_hex(8)
    image_extension = link.split('.')[-1]
    image_extension = image_extension.split('?')[0]
    image_path = os.path.join(imgs_folder, f'{image_hash}.{image_extension}')
    with open(image_path, "wb") as file:
        for chunk in res:
            file.write(chunk)

    sleep(2)
    return image_path


def crop_image(image_path: str):
    """ Remove empty area from image

    Args:
        image_path (str): Path of image to crop
        
    Returns:
        bool: True if image was cropped, False if not
    """

    try:
        image = Image.open(image_path)
        a = np.array(image)[:, :, :3]  # keep RGB only
        m = np.any(a != [255, 255, 255], axis=2)
        coords = np.argwhere(m)
        y0, x0, y1, x1 = *np.min(coords, axis=0), *np.max(coords, axis=0)
        crop_data = (x0, y0, x1 + 1, y1 + 1)
        image_crop = image.crop(crop_data)
        image_crop.save(image_path)
    except Exception:
        return False
    
    return True
