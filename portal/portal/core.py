# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, session, redirect
from oslo_log import log
from oslo_config import cfg

from portal.auth import except_wrap, login_required
from portal.common.utils import convert_unix_timestamp_to_datetime_str
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


@portal_page.route('/agentsinfo.html', methods=['GET'])
@except_wrap
@login_required
def show_agentsinfo_page():
    agents = ProtobufProxy().list_agents()
    __check_rpc_status(agents, 'ProtobufProxy().list_agents()')
    agents_parsed_data = []
    for agent in agents.agents:
        a = dict()
        a['type'] = agent.type
        a['ip'] = agent.ip
        if agent.has_sess == 0:
            a['has_sess'] = '是'
        else:
            a['has_sess'] = '否'
        a['last_sync_db_time'] = convert_unix_timestamp_to_datetime_str(
            agent.last_sync_db_time)
        a['last_heartbeat_time'] = convert_unix_timestamp_to_datetime_str(
            agent.last_heartbeat_time)
        a['last_sync_time'] = convert_unix_timestamp_to_datetime_str(
            agent.last_sync_time)
        a['applications_size'] = len(agent.applications)
        agents_parsed_data.append(a)
    return render_template('agentsinfo.html', resource_class='agentsinfo',
                           agents=agents_parsed_data)


@portal_page.route('/agentsinfo/<ip>/applications.html', methods=['GET'])
@except_wrap
@login_required
def show_agentsinfo_applications_page(ip):
    agents = ProtobufProxy().list_agents()
    __check_rpc_status(agents, 'ProtobufProxy().list_agents()')
    applications = []
    for agent in agents.agents:
        if agent.ip == ip:
            applications = agent.applications
            break
    return render_template('agentsinfo_applications.html',
                           resource_class='agentsinfo',
                           applications=applications)
