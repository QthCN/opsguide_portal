# -*- coding: utf-8 -*-
import datetime
import os

import eventlet
from eventlet import wsgi
from oslo_config import cfg
from flask import Flask, render_template, session, Blueprint
import pbr.version

from portal import config
from portal.login.core import login_page
from portal.www.core import portal_page

CONF = cfg.CONF

common_page = Blueprint('common_page', __name__,
                        template_folder='../templates')


@common_page.route('/404.html', methods=['GET'])
def show_404():
    return render_template('404.html', resource_class='404')


@common_page.route('/500.html', methods=['GET'])
def show_500():
    return render_template('500.html', resource_class='500')


_APP = None

MODULES = [
    (portal_page, ''),
    (login_page, ''),
    (common_page, '')
]


def configure_app(app):
    # FIXME(tianhuan): looks like blueprints is conflict with this statement.
    #app.config['SERVER_NAME'] = CONF.server.address
    pass


def configure_logging(app):
    # oslo will config logging
    pass


def configure_blueprints(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)


def configure_exception_pages(app):
    pass


def make_app(do_config=False):
    global _APP
    if _APP and do_config is False:
        return _APP

    app = Flask(__name__, template_folder="../templates")
    app.secret_key = 'ljaslfjyhdkafjljcsajdhjh123jdk12'

    if do_config:
        configure_app(app)
        configure_logging(app)
        configure_blueprints(app, MODULES)
        configure_exception_pages(app)

    _APP = app
    return app


# it seems like flask need a global app at very first of the program.
# so just call make_app() to create one.
app = make_app()


def before_run(possible_topdir, conf_dir="etc",
               conf_file="portal.conf"):
    dev_conf = os.path.join(possible_topdir,
                            conf_dir,
                            conf_file)
    config_files = None
    if os.path.exists(dev_conf):
        config_files = [dev_conf]

    config.configure(
        version=pbr.version.VersionInfo("portal").version_string(),
        config_files=config_files,
    )

    app = make_app(do_config=True)
    app._static_folder = os.path.join(possible_topdir, 'portal',
                                      'static')
    app.permanent_session_lifetime = datetime.timedelta(hours=1)

    @app.before_request
    def before_request():
        session.permanent = True

    # set 404 page
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    # set 500 page
    @app.errorhandler(500)
    def page_not_found(error):
        return render_template('500.html'), 500

    return app


def run(possible_topdir='', conf_dir="etc", conf_file="portal.conf"):
    app = before_run(possible_topdir)
    eventlet.patcher.monkey_patch(os=False, select=True, socket=True,
                                  thread=False, time=True,
                                  psycopg=False, MySQLdb=False)
    wsgi.server(eventlet.listen(('', int(CONF.server.port))), app)
