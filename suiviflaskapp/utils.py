import os
import re
import random
from PIL import Image
from datetime import datetime
#  random.randint(0, 999999)


def process_image(file, directory):
    filename = os.path.splitext(file.filename)[0].replace(' ', '')
    ext = os.path.splitext(file.filename)[1]
    if ext.lower() not in ('.png', '.jpg', '.jpeg'):
        return None
    image = Image.open(file)
    width, height = image.size
    ratio = 1000/width
    width *= ratio
    height *= ratio
    image = image.resize((int(width), int(height)))
    fullname = '%s%s%s' % (directory, filename, ext)
    image.save(fullname, optimize=True)
    return '%s%s' % (filename, ext)


def rotate_image(file_path):
    im = Image.open(file_path)
    im = im.transpose(Image.ROTATE_90)
    im.save(file_path)


def personalize(obs, child):
    obs = re.sub(r"[Ll]’enfant", child.firstname, obs)
    obs = re.sub(r"[Ll]’élève", child.firstname, obs)
    if child.gender == 'F':
        obs = re.sub(r"([A-Za-zé]+)_(e )", r"\1"+r"\2", obs)
        obs = re.sub(r"([A-Za-zé]+)_([A-Za-zé]+)", r"\2", obs)
    else:
        obs = re.sub(r"([A-Za-zé]+)_e ", r"\1 ", obs)
        obs = re.sub(r"([A-Za-zé]+)_([A-Za-zé]+)", r"\1", obs)
    return obs


def check_text(text):
    text = text.strip()
    text = text.replace("'", "’")
    return text


def school_year(d):
    csy = ''
    if d.month in [9, 10, 11, 12]:
        csy = '%d-%d' % (d.year, d.year+1)
    else:
        csy = '%d-%d' % (d.year-1, d.year)
    return csy

