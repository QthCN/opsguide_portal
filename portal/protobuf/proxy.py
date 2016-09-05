# -*- coding: utf-8 -*-

from oslo_log import log
from oslo_config import cfg

from portal.exceptions import RPCFailedException
import portal.protobuf.ogp_msg_pb2 as msg
from portal.service import MSG_TYPE, Service


LOG = log.getLogger(__name__)
CONF = cfg.CONF


class ProtobufProxy(object):

    def __init__(self):
        self.__s = Service()

    def list_applications(self):
        msg_type, msg_data = self.__s.send_msg('PO_PORTAL_GET_APPS_REQ')
        applications_list = msg.ControllerApplicationsList()
        applications_list.ParseFromString(msg_data)
        return applications_list

    def list_agents(self):
        msg_type, msg_data = self.__s.send_msg('PO_PORTAL_GET_AGENTS_REQ')
        agents_list = msg.ControllerAgentList()
        agents_list.ParseFromString(msg_data)
        return agents_list

    def publish_app(self, app_id, app_version, runtime_name,
                    app_cfg=None, hints=None):
        publish_app_req = msg.PublishAppReq()
        publish_app_req.app_id = app_id
        publish_app_req.app_version = app_version
        publish_app_req.runtime_name = runtime_name

        if app_id == -1 or app_version == '' or runtime_name == '':
            raise TypeError()

        if hints is not None:
            if 'da_ip' in hints:
                publish_app_req.hints.da_ip = hints['da_ip']

        if app_cfg is not None:
            if 'ports' in app_cfg:
                for port in app_cfg['ports']:
                    port_ = publish_app_req.app_cfg.ports.add()
                    port_.private_port = port['private_port']
                    port_.public_port = port['public_port']
                    port_.type = port['type']
            if 'volumes' in app_cfg:
                for volume in app_cfg['volumes']:
                    volume_ = publish_app_req.app_cfg.volumes.add()
                    volume_.docker_volume = volume['docker_volume']
                    volume_.host_volume = volume['host_volume']
            if 'dns' in app_cfg:
                for dns in app_cfg['dns']:
                    dns_ = publish_app_req.app_cfg.dns.add()
                    dns_.dns = dns['dns']
                    dns_.address = dns['address']
            if 'extra_cmd' in app_cfg:
                publish_app_req.app_cfg.extra_cmd = app_cfg['extra_cmd']

        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_PUBLISH_APP_REQ', publish_app_req)
        publish_app_res = msg.PublishAppRes()
        publish_app_res.ParseFromString(msg_data)
        return publish_app_res

    def remove_version(self, uniq_id):
        remove_ver_req = msg.RemoveAppVerReq()
        remove_ver_req.uniq_id = uniq_id
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_REMOVE_APPVER_REQ', remove_ver_req)
        remove_ver_res = msg.RemoveAppVerRes()
        remove_ver_res.ParseFromString(msg_data)
        return remove_ver_res

    def upgrade_version(self, uniq_id, version, runtime_name):
        upgrade_ver_req = msg.UpgradeAppVerReq()
        upgrade_ver_req.old_ver_uniq_id = uniq_id
        upgrade_ver_req.new_version = version
        upgrade_ver_req.runtime_name = runtime_name
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_UPGRADE_APPVER_REQ', upgrade_ver_req)
        upgrade_ver_res = msg.UpgradeAppVerRes()
        upgrade_ver_res.ParseFromString(msg_data)
        return upgrade_ver_res

    def add_service(self, app_id, service_type,
                    # service_type == PORT_SERVICE
                    service_port=None, private_port=None):
        add_service_req = msg.AddServiceReq()
        if service_type == 'PORT_SERVICE':
            if service_port is None:
                raise TypeError("service_port is None")
            add_service_req.app_id = app_id
            add_service_req.service_type = 'PORT_SERVICE'
            add_service_req.port_service_body.service_port = int(service_port)
            if private_port is not None:
                add_service_req.port_service_body.private_port = \
                    int(private_port)
        else:
            LOG.error("{0} is invalid".format(service_type))
            raise TypeError()

        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_ADD_SERVICE_REQ', add_service_req
        )
        add_service_res = msg.AddServiceRes()
        add_service_res.ParseFromString(msg_data)
        return add_service_res

    def delete_service(self, service_id):
        del_service_req = msg.DelServiceReq()
        del_service_req.service_id = service_id
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_DEL_SERVICE_REQ', del_service_req
        )
        del_service_res = msg.DelServiceRes()
        del_service_res.ParseFromString(msg_data)
        return del_service_res

    def list_services(self):
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_LIST_SERVICES_REQ'
        )
        list_services_res = msg.ListServicesRes()
        list_services_res.ParseFromString(msg_data)
        return list_services_res

    def list_services_details(self):
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_LIST_SERVICES_DETAIL_REQ'
        )
        services_detail_res = msg.ServiceSyncData()
        services_detail_res.ParseFromString(msg_data)
        return services_detail_res

    def list_appcfgs(self):
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_LIST_APP_CFG_REQ'
        )
        list_appcfgs_res = msg.DASyncAppsCFGRes()
        list_appcfgs_res.ParseFromString(msg_data)
        return list_appcfgs_res

    def update_appcfg(self, app_id, path, content):
        update_appcfg_req = msg.PortalUpdateAppCFGReq()
        update_appcfg_req.app_id = int(app_id)
        update_appcfg_req.path = path
        update_appcfg_req.content = content
        msg_type, msg_data = self.__s.send_msg(
            'PO_PORTAL_UPDATE_APP_CFG_REQ', update_appcfg_req
        )
        update_appcfg_res = msg.PortalUpdateAppCFGRes()
        update_appcfg_res.ParseFromString(msg_data)
        return update_appcfg_res





