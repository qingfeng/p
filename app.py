import os
import uuid
import Image
import cropresize

from flask import Flask, request, redirect, url_for, abort
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template
from plim import preprocessor
from dae.api import permdir

DOMAIN = "http://p.dapps.douban.com"
UPLOAD_FOLDER = permdir.get_permdir()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'psd'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAKO_PREPROCESSOR'] = preprocessor
app.config['MAKO_TRANSLATE_EXCEPTIONS'] = False
app.debug = True
mako = MakoTemplates(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def gen_filename(suffix):
    return "%s.%s" % (uuid.uuid1().hex, suffix)

@app.route('/r/<img_hash>')
def rsize(img_hash):
    w = request.args.get('w')
    h = request.args.get('h')
    if w and h:
        file = "%s/%s" % (app.config['UPLOAD_FOLDER'], img_hash)
        original_suffix = img_hash.rpartition('.')[-1]
        filename = gen_filename(original_suffix)
        img = cropresize.crop_resize(Image.open(file), (int(w), int(h)))
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "%s/i/%s" % (DOMAIN, filename)
    return about(400)

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        file = request.files['file']
        w = request.form.get('w')
        h = request.form.get('h')
        if file and allowed_file(file.filename):
            original_suffix = file.filename.rpartition('.')[-1]
            filename = gen_filename(original_suffix)
            if w and h:
                img = cropresize.crop_resize(Image.open(file), (int(w), int(h)))
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "/p/%s" % filename
        return abort(400)
    return render_template('index.html', **locals())

@app.route('/p/<filename>')
def p(filename):
    domain = DOMAIN
    return render_template('success.html', **locals())
