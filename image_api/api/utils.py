from PIL import Image
from django.db.models import ImageField
from io import BytesIO
from django.core.files.base import File
from pathlib import Path



def resize_image(img: Image, height: int) -> Image:
    '''Returns resized image with given height, saves original aspect ratio'''
    aspect_ratio = img.width/img.height
    width = int(height * aspect_ratio)
    return img.resize((width, height))


def get_resized_image(image: ImageField, height: int) -> File:
    '''Returns file containing resized image'''
    img = Image.open(image)
    buffer = BytesIO()

    new_image = resize_image(img, height)
    new_image.save(buffer, format=img.format)

    return File(buffer, name=image.name)


def delete_file(path: str) -> None:
    try:
        path = Path(path)
        path.unlink(missing_ok=True)
    except:
        pass    # code smell, but nothing to do here - file didn't exist