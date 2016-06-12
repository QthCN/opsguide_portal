# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, session, redirect
from oslo_log import log
from oslo_config import cfg

from portal.auth import except_wrap, login_required
from portal.exceptions import RPCContentException
from portal.protobuf.proxy import ProtobufProxy

LOG = log.getLogger(__name__)
CONF = cfg.CONF


portal_page = Blueprint('portal_page', __name__,
                        template_folder='../templates')


def __check_rpc_status(obj, item):
    if obj.header.rc != 0:
        LOG.error("{0} error, rc: {1}, msg: {2}".format(
            item,
            obj.header.rc,
            obj.header.msg
        ))
        raise RPCContentException


@portal_page.route('/', methods=['GET'])
@portal_page.route('/portal.html', methods=['GET'])
@except_wrap
@login_required
def show_home_page():
    return render_template('base.html', resource_class='overview')


@portal_page.route('/appsinfo.html', methods=['GET'])
@except_wrap
@login_required
def show_appsinfo_page():
    applications = ProtobufProxy().list_applications()
    __check_rpc_status(applications, 'ProtobufProxy().list_applications()')
    return render_template('appsinfo.html', resource_class='appsinfo',
                           applications=applications)


@portal_page.route('/appsinfo/<app_id>/versions.html', methods=['GET'])
@except_wrap
@login_required
def show_appsinfo_versions_page(app_id):
    applications = ProtobufProxy().list_applications()
    __check_rpc_status(applications, 'ProtobufProxy().list_applications()')
    versions = []
    for a in applications.applications:
        if a.id == int(app_id):
            versions = a.versions
            break
    return render_template('appsinfo_versions.html', resource_class='appsinfo',
                           versions=versions)
