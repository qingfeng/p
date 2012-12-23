import os
import uuid
import Image
import cropresize

from flask import Flask, request, redirect, url_for, abort
from dae.api import permdir

DOMAIN = "http://p.dapps.douban.com"
UPLOAD_FOLDER = permdir.get_permdir()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
        w = request.form['w']
        h = request.form['h']
        if file and allowed_file(file.filename):
            original_suffix = file.filename.rpartition('.')[-1]
            filename = gen_filename(original_suffix)
            if w and h:
                img = cropresize.crop_resize(Image.open(file), (int(w), int(h)))
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "%s/i/%s" % (DOMAIN, filename)
        return abort(400)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    Command line: ``curl -F file=@"/tmp/1.png" http://p.dapps.douban.com/``<br>
    Command line: ``curl -F file=@"/tmp/1.png" -F w=100 -F h=100 http://p.dapps.douban.com/``<br>
    Resize image: ``http://p.dapps.douban.com/r/img_hash.jpg?w=300&h=200``<br>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         w:<input type=text name=w>
         h:<input type=text name=h>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.run()
