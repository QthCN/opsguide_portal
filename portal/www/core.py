# -*- coding: utf-8 -*-

import json

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
            obj.header.message
        ))
        raise RPCContentException(obj.header.message)


def gen_result(data=None, rc=0, msg=""):
    return json.dumps(dict(
        data=data,
        rc=rc,
        msg=msg
    ))


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


@portal_page.route('/pubmgr.html', methods=['GET'])
@except_wrap
@login_required
def show_pubmgr_page():
    applications = ProtobufProxy().list_applications()
    __check_rpc_status(applications, 'ProtobufProxy().list_applications()')
    app_versions = dict()
    for app in applications.applications:
        if app.name not in app_versions:
            app_versions[app.name] = []
        for ver in app.versions:
            app_versions[app.name].append(ver.version)
    app_versions = json.dumps(app_versions)

    agents = ProtobufProxy().list_agents()
    __check_rpc_status(agents, 'ProtobufProxy().list_agents()')
    applications_parsed_data = []
    for agent in agents.agents:
        for app in agent.applications:
            a = dict()
            a['agent_type'] = agent.type
            a['agent_ip'] = agent.ip
            if agent.has_sess == 0:
                a['agent_has_sess'] = '是'
            else:
                a['agent_has_sess'] = '否'
            a['agent_last_sync_db_time'] = \
                convert_unix_timestamp_to_datetime_str(agent.last_sync_db_time)
            a['agent_last_heartbeat_time'] = \
                convert_unix_timestamp_to_datetime_str(
                    agent.last_heartbeat_time)
            a['agent_last_sync_time'] = \
                convert_unix_timestamp_to_datetime_str(
                    agent.last_sync_time)
            a['agent_applications_size'] = len(agent.applications)

            a['app_name'] = app.app_name
            a['app_version'] = app.app_version
            a['app_id'] = app.app_id
            a['uniq_id'] = app.uniq_id
            a['runtime_name'] = app.runtime_name
            a['status'] = app.status
            applications_parsed_data.append(a)
            applications_parsed_data = sorted(applications_parsed_data,
                                              key=lambda x: x['agent_ip'])
    return render_template('pubmgr.html', resource_class='pubmgr',
                           applications_parsed_data=applications_parsed_data,
                           app_versions=app_versions)


@portal_page.route('/pubmgr/publish', methods=['POST'])
@except_wrap
@login_required
def do_publish():
    request_json = request.form.get('request_json', None)

    try:
        request_data = json.loads(request_json)
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="invalid json")

    try:
        publish_result = ProtobufProxy().publish_app(
            request_data.get('app_id', -1),
            request_data.get('app_version', ''),
            request_data.get('runtime_name', ''),
            request_data.get('app_cfg', None),
            request_data.get('hints', None)
        )
        __check_rpc_status(publish_result, 'ProtobufProxy().publish_app()')
    except TypeError as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="JSON content error")
    except RPCContentException as e:
        LOG.exception(e)
        return gen_result(rc=1, msg=e.args[0])
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="RPC error")
    return gen_result()


@portal_page.route('/pubmgr/remove/<uniq_id>', methods=['POST'])
@except_wrap
@login_required
def do_remove(uniq_id):
    try:
        publish_result = ProtobufProxy().remove_version(int(uniq_id))
        __check_rpc_status(publish_result, 'ProtobufProxy().remove_version()')
    except RPCContentException as e:
        LOG.exception(e)
        return gen_result(rc=1, msg=e.args[0])
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="RPC error")
    return gen_result()


@portal_page.route('/pubmgr/upgrade/<uniq_id>', methods=['POST'])
@except_wrap
@login_required
def do_upgrade(uniq_id):
    try:
        version = request.form.get('new_version', '')
        runtime_name = request.form.get('runtime_name', '')
        publish_result = ProtobufProxy().upgrade_version(
            int(uniq_id), version, runtime_name)
        __check_rpc_status(publish_result, 'ProtobufProxy().upgrade_version()')
    except RPCContentException as e:
        LOG.exception(e)
        return gen_result(rc=1, msg=e.args[0])
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="RPC error")
    return gen_result()


@portal_page.route('/services.html', methods=['GET'])
@except_wrap
@login_required
def show_services_page():
    services_list = ProtobufProxy().list_services()
    __check_rpc_status(services_list, 'ProtobufProxy().services_list()')
    return render_template('services.html', resource_class='services',
                           services_list=services_list)


@portal_page.route('/services/add', methods=['POST'])
@except_wrap
@login_required
def do_add_service():
    request_json = request.form.get('request_json', None)

    try:
        request_data = json.loads(request_json)
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="invalid json")

    try:
        add_result = ProtobufProxy().add_service(
            request_data.get('app_id', -1),
            request_data.get('service_type', ''),
            request_data.get('service_port', -1),
            request_data.get('private_port', -1),
        )
        __check_rpc_status(add_result, 'ProtobufProxy().add_service()')
    except TypeError as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="JSON content error")
    except RPCContentException as e:
        LOG.exception(e)
        return gen_result(rc=1, msg=e.args[0])
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="RPC error")
    return gen_result()


@portal_page.route('/services/remove/<service_id>', methods=['POST'])
@except_wrap
@login_required
def do_service_remove(service_id):
    try:
        remove_result = ProtobufProxy().delete_service(int(service_id))
        __check_rpc_status(remove_result, 'ProtobufProxy().delete_service()')
    except RPCContentException as e:
        LOG.exception(e)
        return gen_result(rc=1, msg=e.args[0])
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="RPC error")
    return gen_result()


@portal_page.route('/services/detail/<service_id>', methods=['GET'])
@except_wrap
@login_required
def show_service_detail_page(service_id):
    services_detail = ProtobufProxy().list_services_details()
    __check_rpc_status(services_detail,
                       'ProtobufProxy().list_services_details()')
    service = None
    for s in services_detail.infos:
        if s.service_id == int(service_id):
            service = s
            break
    return render_template('services_detail.html',
                           resource_class='services',
                           services_details=s)


@portal_page.route('/cfgs.html', methods=['GET'])
@except_wrap
@login_required
def show_cfgs_page():
    cfg_list = ProtobufProxy().list_appcfgs()
    __check_rpc_status(cfg_list, 'ProtobufProxy().list_appcfgs()')
    applications = ProtobufProxy().list_applications()
    __check_rpc_status(applications, 'ProtobufProxy().list_applications()')
    return render_template('cfgs.html', resource_class='cfgs',
                           cfg_list=cfg_list, applications=applications)


@portal_page.route('/cfgs/update', methods=['POST'])
@except_wrap
@login_required
def do_update_cfgs():
    content = request.form.get('content', None)
    app_id = request.form.get('app_id', None)
    path = request.form.get('path', None)

    try:
        app_id = int(app_id)
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="invalid app_id")

    try:
        update_result = ProtobufProxy().update_appcfg(app_id, path, content)
        __check_rpc_status(update_result, 'ProtobufProxy().update_appcfg()')
    except RPCContentException as e:
        LOG.exception(e)
        return gen_result(rc=1, msg=e.args[0])
    except Exception as e:
        LOG.exception(e)
        return gen_result(rc=1, msg="RPC error")
    return gen_result()


@portal_page.route('/cfgs/content/<app_name>', methods=['GET'])
@except_wrap
@login_required
def show_cfg_content_page(app_name):
    content = u'未找到应用对应的配置文件信息'
    cfg_list = ProtobufProxy().list_appcfgs()
    __check_rpc_status(cfg_list, 'ProtobufProxy().list_appcfgs()')
    for cfg in cfg_list.cfgs:
        if cfg.app_name == app_name:
            content = cfg.content
            break
    return render_template('cfg_content.html', resource_class='cfgs',
                           content=content)
