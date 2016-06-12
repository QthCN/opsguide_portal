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


