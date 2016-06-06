# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, session, redirect
from oslo_log import log
from oslo_config import cfg

from portal.auth.core import SimpleAuth
from portal.auth import except_wrap
from portal.exceptions import AuthFailedException

LOG = log.getLogger(__name__)
CONF = cfg.CONF


login_page = Blueprint('login_page', __name__,
                       template_folder='../templates')


@login_page.route('/login.html', methods=['GET'])
def show_loginpage():
    from_url = request.args.get('from', '/')
    return render_template('login.html', from_url=from_url)


@login_page.route('/login.html', methods=['POST'])
def handle_login_request():
    username = request.form.get('inputName', '')
    password = request.form.get('inputPassword', '')
    from_url = request.form.get('from_url', '/')
    sa = SimpleAuth()
    try:
        token = sa.get_token_by_auth(username, password)
        session['username'] = username
        session['token'] = token
        return redirect(from_url)
    except AuthFailedException as e:
        LOG.error("{0} use wrong auth info to signin.".format(username))
        return render_template('login.html', from_url=from_url)


@login_page.route('/logout.html', methods=['GET'])
def handle_logout_request():
    session['username'] = '_NOUSER_'
    session['token'] = '_NOTOKEN_'
    return render_template('login.html')
