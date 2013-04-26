import os

def is_image(filename):
    fname, ext = os.path.splitext(filename)
    return ext in ('.png', '.jpg', '.jpeg', '.gif')
    
def is_pdf(filename):
    fname, ext = os.path.splitext(filename)
    return ext in ('.pdf')
    
def is_psd(filename):
    fname, ext = os.path.splitext(filename)
    return ext in ('.psd')
