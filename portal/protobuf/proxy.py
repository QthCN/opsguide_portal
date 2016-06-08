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
        self.__service = Service()

    def list_applications(self):
        msg_type, msg_data = self.__service.send_msg('PO_PORTAL_GET_APPS_REQ')
        applications_list = msg.ControllerApplicationsList()
        applications_list.ParseFromString(msg_data)


