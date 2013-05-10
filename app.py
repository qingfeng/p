import os
import uuid
import Image
import cropresize

from flask import Flask, request, redirect, url_for, abort, jsonify
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
    return abort(400)

@app.route('/a/<img_hash>')
def affine(img_hash):
    w = request.args.get('w')
    h = request.args.get('h')

    a = request.args.get('a')
    a = map(float, a.split(','))

    if w and h and a and len(a) == 6:
        size = (int(w), int(h))
        file = "%s/%s" % (app.config['UPLOAD_FOLDER'], img_hash)
        original_suffix = img_hash.rpartition('.')[-1]
        filename = gen_filename(original_suffix)
        img = Image.open(file).transform(size, Image.AFFINE, a, Image.BILINEAR)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "%s/i/%s" % (DOMAIN, filename)
    return abort(400)

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

@app.route('/t', methods=['POST'])
def terminal():
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
        return "%s/i/%s" % (DOMAIN, filename)
    return 'error upload'

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/j', methods=['GET', 'POST'])
def j():
    file = request.files['file']
    if file and allowed_file(file.filename):
        original_suffix = file.filename.rpartition('.')[-1]
        filename = gen_filename(original_suffix)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'url':"%s/i/%s" % (DOMAIN, filename)})
    return abort(400)

@app.route('/p/<filename>')
def p(filename):
    domain = DOMAIN
    return render_template('success.html', **locals())
