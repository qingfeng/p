#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi


import os
from plim import preprocessor

DAE_ENV = os.environ.get('DAE_ENV')
HEROKU_ENV = HEROKU_DB = os.environ.get('DATABASE_URL')
YUN_CDN = None

if DAE_ENV:
    from dae.api import permdir
    from dae.api.mysql import get_mysql_conn_params

    _SQL_PARAMS = get_mysql_conn_params()
    UPLOAD_FOLDER = permdir.get_permdir()
elif HEROKU_ENV:
    import urlparse

    urlparse.uses_netloc.append("mysql")
    url = urlparse.urlparse(HEROKU_DB)

    _SQL_PARAMS = {
        'protocol': url.scheme,
        'passwd': url.password,
        'host': url.hostname,
        'db': url.path[1:],
        'port': 3306,
        'user': url.username,
    }
    UPLOAD_FOLDER = 'large'
    import upyun
    UPYUN_BUCKET = os.environ.get('UPYUN_BUCKET')
    UPYUN_USER = os.environ.get('UPYUN_USER')
    UPYUN_PASSWORD = os.environ.get('UPYUN_PASSWORD')
    YUN_CDN = upyun.UpYun(UPYUN_BUCKET, UPYUN_USER, UPYUN_PASSWORD, timeout=30, endpoint=upyun.ED_AUTO)
    YUN_CDN_URL = "http://%s.b0.upaiyun.com/%s/%%s" % (UPYUN_BUCKET, UPLOAD_FOLDER)
else:
    _SQL_PARAMS = {
        'protocol': 'mysql',
        'passwd': '',
        'host': '127.0.0.1',
        'db': 'p',
        'port': 3306,
        'user': 'root',
        }
    UPLOAD_FOLDER = 'upload_temp'

DEBUG = True
MAX_CONTENT_LENGTH = 32 * 1024 * 1024
MAKO_PREPROCESSOR = preprocessor
MAKO_TRANSLATE_EXCEPTIONS = False
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (_SQL_PARAMS['protocol'], \
                                                      _SQL_PARAMS['user'], \
                                                      _SQL_PARAMS['passwd'], \
                                                      _SQL_PARAMS['host'], \
                                                      _SQL_PARAMS['port'], \
                                                      _SQL_PARAMS['db'])

try:
    from local_config import *
except Exception:
    pass
