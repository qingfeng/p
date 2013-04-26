import os

def is_image(filename):
    fname, ext = os.path.splitext(filename)
    return ext in ('.png', '.jpg', '.jpeg', '.gif')
