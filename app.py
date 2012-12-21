import os
import uuid
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
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

@app.route("/i")
def i():
    return "Hello World!"

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = gen_filename()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "http://p.dapps.douban.com/i/%s" % filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.run()
