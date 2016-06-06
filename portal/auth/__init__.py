# -*- coding: utf-8 -*-

from functools import wraps

from flask import session, redirect, render_template, request
from oslo_config import cfg
from oslo_log import log

from portal.exceptions import AuthFailedException


LOG = log.getLogger(__name__)
CONF = cfg.CONF


def login_required(f):
    @wraps(f)
    def _auth_check(*args, **kwargs):
        if session.get('username', None) and session['username'] != '_NOUSER_':
            return f(*args, **kwargs)
        else:
            url = request.base_url
            return redirect('/login.html?from={0}'.format(url))
    return _auth_check


def except_wrap(f):
    @wraps(f)
    def _except_wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            LOG.exception(e)
            if isinstance(e, AuthFailedException):
                session['username'] = '_NOUSER_'
                session['token'] = '_NOTOKEN_'
                return render_template('login.html')
            return redirect('500.html')
    return _except_wrap
