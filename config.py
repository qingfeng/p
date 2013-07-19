#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi


from plim import preprocessor

from dae.api import permdir
from dae.api.mysql import get_mysql_conn_params

_SQL_PARAMS = get_mysql_conn_params()

DEBUG = False
UPLOAD_FOLDER = permdir.get_permdir()
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
MAKO_PREPROCESSOR = preprocessor
MAKO_TRANSLATE_EXCEPTIONS = False
SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%s/%s" % (_SQL_PARAMS['user'], \
                                                      _SQL_PARAMS['passwd'], \
                                                      _SQL_PARAMS['host'], \
                                                      _SQL_PARAMS['port'], \
                                                      _SQL_PARAMS['db'])

try:
    from local_config import *
except Exception:
    pass
