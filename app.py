# -*- coding: utf-8 -*-

import os
import uuid
import magic
import Image
import urllib
import cropresize
from random import choice
from string import digits
from string import ascii_uppercase
from string import ascii_lowercase
from datetime import datetime

from flask import abort
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import send_file
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template
from flask.ext.sqlalchemy import SQLAlchemy

from mimes import IMAGE_MIMES
from mimes import AUDIO_MIMES
from mimes import VIDEO_MIMES

RANDOM_SEQ = ascii_uppercase + ascii_lowercase + digits

app = Flask(__name__)
app.config.from_object("config")
mako = MakoTemplates(app)
db = SQLAlchemy(app)

command_agent_keys = ['curl', 'wget']

class PasteFile(db.Model):
    __tablename__ = "PasteFile"
    id            = db.Column(db.Integer, primary_key = True)
    filename      = db.Column(db.String(5000), nullable = False)
    filehash      = db.Column(db.String(128), nullable = False, unique = True)
    uploadTime    = db.Column(db.DateTime, nullable = False)
    mimetype      = db.Column(db.String(256), nullable = False)
    symlink       = db.Column(db.String(50, collation = 'utf8_bin'), nullable = False, unique = True) # collation is for case-sensitive select
    size          = db.Column(db.Integer, nullable = False)

    def __init__(self, filename = "", mimetype = "application/octet-stream", size = 0, filehash = None, symlink = None):
        self.uploadTime = datetime.now()
        self.mimetype   = mimetype
        self.size       = int(size)
        self.filehash   = filehash if filehash else self._hash_filename(filename)
        self.filename   = filename if filename else self.filehash
        self.symlink    = symlink  if symlink  else self._gen_symlink()

    @staticmethod
    def _hash_filename(filename):
        _, _, suffix = filename.rpartition('.')
        return "%s.%s" % (uuid.uuid4().hex, suffix)

    @staticmethod
    def _gen_symlink():
        return "".join(choice(RANDOM_SEQ) for x in range(6))

    @classmethod
    def get_by_filehash(cls, filehash):
        return cls.query.filter_by(filehash = filehash).first()

    @classmethod
    def get_by_symlink(cls, symlink):
        return cls.query.filter_by(symlink = symlink).first()

    @classmethod
    def create_by_uploadFile(cls, uploadedFile):
        rst      = cls(uploadedFile.filename, uploadedFile.mimetype, 0) # emmm. I'll fill this value later.
        uploadedFile.save(rst.path)
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        return rst

    @classmethod
    def create_file_after_crop(cls, uploadedFile, width, height):
        assert uploadedFile.is_image, TypeError("Unsupported Image Type.")

        img      = cropresize.crop_resize(Image.open(uploadedFile), (int(width), int(height)))
        rst      = cls(uploadedFile.filename, uploadedFile.mimetype, 0)
        img.save(rst.path)

        filestat = os.stat(rst.path) 
        rst.size = filestat.st_size

        return rst

    @classmethod
    def create_by_old_paste(cls, filehash, symlink):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filehash)
        mimetype = magic.from_file(filepath, mime = True)
        filestat = os.stat(filepath)
        size     = filestat.st_size

        rst = cls(filehash, mimetype, size, filehash = filehash, symlink = symlink)
        return rst

    @property
    def path(self):
        return os.path.join(app.config["UPLOAD_FOLDER"], self.filehash)

    @property
    def url_i(self):
        return "http://{host}/i/{filehash}".format(host = request.host, filehash = self.filehash)

    @property
    def url_p(self):
        return "http://{host}/p/{filehash}".format(host = request.host, filehash = self.filehash)

    @property
    def url_s(self):
        return "http://{host}/s/{symlink}".format(host = request.host, symlink = self.symlink)

    @property
    def url_d(self):
        return "http://{host}/d/{filehash}".format(host = request.host, filehash = self.filehash)

    @property
    def quoteurl(self):
        return urllib.quote(self.url_p)

    @classmethod
    def create_by_img(cls, img, filename, mimetype):
        rst      = cls(filename, mimetype, 0)
        img.save(rst.path)
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        return rst

    @classmethod
    def rsize(cls, oldPaste, weight, height):
        assert oldPaste.is_image

        img = cropresize.crop_resize(Image.open(oldPaste.path), (int(weight), int(height)))

        return cls.create_by_img(img, oldPaste.filename, oldPaste.mimetype)

    @classmethod
    def affine(cls, oldPaste, w, h, a):
        assert oldPaste.is_image

        img_size = (int(w), int(h))
        img = Image.open(oldPaste.path).transform(img_size, Image.AFFINE, a, Image.BILINEAR)

        return cls.create_by_img(img, oldPaste.filename, oldPaste.mimetype)

    @property
    def is_image(self):
        return self.mimetype in IMAGE_MIMES

    @property
    def is_audio(self):
        return self.mimetype in AUDIO_MIMES

    @property
    def is_video(self):
        return self.mimetype in VIDEO_MIMES

    @property
    def is_pdf(self):
        return self.mimetype == "application/pdf"

    @property
    def size_humanize(self):
        if self.size < 1024:
            return "{0} bytes".format(self.size)
        size = self.size / 1024.0
        if size < 1024:
            size = "%.2f" % size
            return size.rstrip("0").rstrip(".") + " KB"
        size = size / 1024.0
        size = "%.2f" % size
        return size.rstrip("0").rstrip(".") + " MB"

    @property
    def type(self):
        may_types = ["image", "pdf", "video", "audio"]
        for t in may_types:
            if getattr(self, "is_" + t):
                return t
        return "binary"

def is_command_line_request(request):
    agent = str(request.user_agent).lower()
    if not agent:
        return True
    for k in command_agent_keys:
        if k in agent:
            return True
    return False

@app.route('/r/<img_hash>')
def rsize(img_hash):
    # TODO: rewrite
    w = request.args['w']
    h = request.args['h']

    oldPaste = PasteFile.get_by_filehash(img_hash)

    if not oldPaste:
        return abort(404)

    newPaste = PasteFile.rsize(oldPaste, w, h)

    return newPaste.url_i

@app.route('/a/<img_hash>')
def affine(img_hash):
    w = request.args['w']
    h = request.args['h']

    a = request.args['a']
    a = map(float, a.split(','))

    if len(a) != 6:
        return abort(400)

    oldPaste = PasteFile.get_by_filehash(img_hash)

    if not oldPaste:
        return abort(404)

    newPaste = PasteFile.affine(oldPaste, w, h, a)

    return newPaste.url_i

@app.route('/d/<filehash>', methods = ["GET"])
def download(filehash):
    pasteFile = PasteFile.get_by_filehash(filehash)
    
    if not pasteFile:
        return abort(404)

    return send_file(open(pasteFile.path, "rb"), \
            mimetype = "application/octet-stream", \
            cache_timeout = 2592000, \
            as_attachment = True, \
            attachment_filename = pasteFile.filename.encode("UTF-8"))

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        uploadedFile = request.files['file']
        w = request.form.get('w')
        h = request.form.get('h')

        # text file treat as binary file.
        # if user wanna post a text file, they would use pastebin / gist. 
        
        if not uploadedFile:
            return abort(400)

        if w and h:
            pasteFile = PasteFile.create_file_after_crop(uploadedFile, w, h)
        else:
            pasteFile = PasteFile.create_by_uploadFile(uploadedFile)
        db.session.add(pasteFile)
        db.session.commit()

        if is_command_line_request(request):
            return pasteFile.url_i

        return jsonify({
            "url_d"    : pasteFile.url_d,  
            "url_i"    : pasteFile.url_i, 
            "url_s"    : pasteFile.url_s, 
            "url_p"    : pasteFile.url_p, 
            "filename" : pasteFile.filename, 
            "size"     : pasteFile.size_humanize, 
            "time"     : str(pasteFile.uploadTime), 
            "type"     : pasteFile.type, 
        })
    return render_template('index.html', **locals())

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/j', methods=['POST'])
def j():
    uploadedFile = request.files['file']

    if uploadedFile:
        pasteFile = PasteFile.create_by_uploadFile(uploadedFile)

        return jsonify({
                "url"             : pasteFile.url_i, 
                "short_url"       : pasteFile.url_s, 
                "origin_filename" : pasteFile.filename, 
                })

    return abort(400)

@app.route('/p/<filehash>')
def preview(filehash):
    pasteFile = PasteFile.get_by_filehash(filehash)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filehash)
    if not pasteFile:
        # check file exists
        if not(os.path.exists(filepath) and (not os.path.islink(filepath))):
            return abort(404)

        linkfile = os.path.join(app.config['UPLOAD_FOLDER'], filehash.replace('.', '_'))
        symlink  = None
        if os.path.exists(linkfile):
            with open(linkfile) as fp:
                symlink = fp.read().strip()

        pasteFile = PasteFile.create_by_old_paste(filehash, symlink)
        db.session.add(pasteFile)
        db.session.commit()

    return render_template('success.html', p = pasteFile, r = request)

@app.route('/s/<symlink>')
def s(symlink):
    pasteFile = PasteFile.get_by_symlink(symlink)

    if not pasteFile:
        return abort(404)

    return redirect(pasteFile.url_p)
