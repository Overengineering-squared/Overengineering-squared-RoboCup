import os
import uuid

from PIL import Image


def convert_png_to_jpg(directory_path, quality):
    files = os.listdir(directory_path)

    for file_name in files:

        if file_name.endswith('.png'):
            img = Image.open(os.path.join(directory_path, file_name))

            rgb_img = img.convert('RGB')

            new_file_name = str(uuid.uuid4()) + '.jpg'

            rgb_img.save(os.path.join(directory_path, new_file_name), quality=quality)

            os.remove(os.path.join(directory_path, file_name))


path = ''
convert_png_to_jpg(path, 100)
