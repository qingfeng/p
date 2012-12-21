import os
import uuid
import Image
import cropresize

from flask import Flask, request, redirect, url_for
from dae.api import permdir

UPLOAD_FOLDER = permdir.get_permdir()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def gen_filename():
    return "%s.jpg" % uuid.uuid1().hex

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        file = request.files['file']
        w = request.form['w']
        h = request.form['h']
        if file and allowed_file(file.filename):
            filename = gen_filename()
            if w and h:
                img = cropresize.crop_resize(Image.open(file), (int(w), int(h)))
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "http://p.dapps.douban.com/i/%s" % filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    Command line: `curl -F file=@"/tmp/1.png" http://p.dapps.douban.com/`<br>
    Command line: `curl -F file=@"/tmp/1.png" -F w=100 -F h=100 http://p.dapps.douban.com/`<br>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         w:<input type=text name=w>
         h:<input type=text name=h>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.run()
