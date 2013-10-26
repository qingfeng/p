P
====

Douban Intra Service [http://p.dapps.douban.com/](http://p.dapps.douban.com/)

Dev
====
```
git clone PROJECT.git
cd PROJECT
virtualenv venv
source venv/bin/activate
pip install -r requirement.txt
mkdir permdir
python app.py
open http://localhost:5000
```

Command Line
====
Example:

 * Command line: ``curl -F file=@"/tmp/1.png" http://p.dapps.douban.com/``
 * Command line: ``curl -F file=@"/tmp/1.png" -F w=100 -F h=100 http://p.dapps.douban.com/``
 * Resize image: ``http://p.dapps.douban.com/r/img_hash.jpg?w=300&h=200``
 * Affine Transformation:
     ``http://p.dapps.douban.com/a/img_hash.jpg?w=300&h=300&a=0.86,0.5,-100,-0.5,0.86,50``
     (Rotate 30 degree clockwise and then translation 100 right, 50 up.)

Mac Desktop
====
Thanks @zhuchongyu [Download](http://d.dapps.douban.com/_upload/DoubanP.zip)
