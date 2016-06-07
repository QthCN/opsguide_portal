# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, session, redirect
from oslo_log import log
from oslo_config import cfg

from portal.auth import except_wrap, login_required

from portal.protobuf.proxy import ProtobufProxy

LOG = log.getLogger(__name__)
CONF = cfg.CONF


portal_page = Blueprint('portal_page', __name__,
                        template_folder='../templates')


@portal_page.route('/', methods=['GET'])
@portal_page.route('/portal.html', methods=['GET'])
@except_wrap
@login_required
def show_homepage():
    ProtobufProxy().list_applications()
    return render_template('base.html', resource_class='overview')
