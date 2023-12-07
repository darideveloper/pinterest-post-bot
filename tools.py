import os
import requests
import secrets

current_folder = os.path.dirname(__file__)
images_folder = os.path.join(current_folder, 'images')


def download_image(link: str) -> str:
    """ Download image and save in "images" folder

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
    image_path = os.path.join(images_folder, f'{image_hash}.{image_extension}')
    with open(image_path, "wb") as file:
        for chunk in res:
            file.write(chunk)

    return image_path