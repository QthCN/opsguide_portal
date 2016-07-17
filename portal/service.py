# -*- coding: utf-8 -*-

import socket
import struct
import time

from oslo_log import log
from oslo_config import cfg

from portal.exceptions import RPCFailedException
import portal.protobuf.ogp_msg_pb2 as msg


LOG = log.getLogger(__name__)
CONF = cfg.CONF


# 依赖controller的消息id定义
MSG_TYPE = {
    # controller
    'CT_PORTAL_GET_APPS_RES': 3,
    'CT_PORTAL_GET_AGENTS_RES': 5,
    'CT_PORTAL_PUBLISH_APP_RES': 6,
    'CT_PORTAL_REMOVE_APPVER_RES': 7,
    'CT_PORTAL_UPGRADE_APPVER_RES': 8,
    'CT_PORTAL_ADD_SERVICE_RES': 9,
    'CT_PORTAL_DEL_SERVICE_RES': 10,
    'CT_PORTAL_LIST_SERVICES_RES': 11,
    'CT_PORTAL_LIST_SERVICES_DETAIL_RES': 15,

    # portal
    'PO_PORTAL_GET_APPS_REQ': 9000,
    'PO_PORTAL_GET_AGENTS_REQ': 9001,
    'PO_PORTAL_PUBLISH_APP_REQ': 9002,
    'PO_PORTAL_REMOVE_APPVER_REQ': 9003,
    'PO_PORTAL_UPGRADE_APPVER_REQ': 9004,
    'PO_PORTAL_ADD_SERVICE_REQ': 9005,
    'PO_PORTAL_DEL_SERVICE_REQ': 9006,
    'PO_PORTAL_LIST_SERVICES_REQ': 9007,
    'PO_PORTAL_LIST_SERVICES_DETAIL_REQ': 9008,
}


class Service(object):

    def __init__(self, address=''):
        if address == '':
            address = CONF.controller.address

        addresses = address.split(':')
        if len(addresses) != 2:
            raise TypeError("address format error.")
        self.__address = address
        self.__ip = addresses[0]
        self.__port = int(addresses[1])

    def send_msg(self, msg_type, protobuf_obj=None, need_resp=True):
        if msg_type not in MSG_TYPE:
            LOG.error('unknown msg_type: {0}'.format(msg_type))
            raise TypeError('unknown msg_type: {0}'.format(msg_type))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.__ip, self.__port))

            # 消息格式: 4个字节的长度(包含类型+数据)+2个字节的类型+数据
            if protobuf_obj is not None:
                msg_body = protobuf_obj.SerializeToString()
                msg_size = 2 + len(msg_body)
            else:
                msg_body = None
                msg_size = 2
            msg_type = MSG_TYPE[msg_type]

            # 发送长度
            sock.send(struct.pack('B', msg_size >> 24 & 255))
            sock.send(struct.pack('B', msg_size >> 16 & 255))
            sock.send(struct.pack('B', msg_size >> 8 & 255))
            sock.send(struct.pack('B', msg_size & 255))
            # 发送类型
            sock.send(struct.pack('B', msg_type >> 8 & 255))
            sock.send(struct.pack('B', msg_type & 255))
            # 发送数据
            if protobuf_obj is not None:
                sock.send(msg_body)

            if need_resp is True:
                # 接收数据
                msg = bytes()
                size_handled = False
                begin_timestamp = time.time()
                # 接下来的读取操作超时时间为5秒
                sock.settimeout(5)
                while True:
                    data = sock.recv(1024)
                    msg += data
                    # 长度头部没有接收完
                    if len(msg) <= 4:
                        continue

                    # 长度头部接收完成,解析该长度
                    if size_handled is False:
                        msg_size = (struct.unpack('B',
                                                  msg[0].to_bytes(
                                                      1, 'little'))[0] << 24) \
                            + (struct.unpack('B',
                                             msg[1].to_bytes(
                                                 1, 'little'))[0] << 16) \
                            + (struct.unpack('B',
                                             msg[2].to_bytes(
                                                 1, 'little'))[0] << 8) \
                            + (struct.unpack('B',
                                             msg[3].to_bytes(
                                                 1, 'little'))[0])
                        msg = msg[4:]
                        size_handled = True

                    # 根据长度头部得到的长度判断整个报文还没有接收完
                    if size_handled is True and len(msg) < msg_size:
                        continue

                    # 已经获取到了完整的报文数据
                    # 获取类型信息
                    msg_type_value = (struct.unpack('B', msg[0].to_bytes(
                        1, 'little'))[0] << 8) \
                        + (struct.unpack('B', msg[1].to_bytes(
                        1, 'little'))[0])
                    msg_type = None
                    # 获取数据部分
                    msg = msg[2:]
                    for k, v in MSG_TYPE.items():
                        if v == msg_type_value:
                            msg_type = k
                            break
                    else:
                        LOG.warn('unknown response msg_type_value: {0}'.format(
                            msg_type_value
                        ))
                    sock.close()
                    # 这里的msg为二进制格式,可以用protobuf的ParseFromString还原
                    return msg_type, msg
            else:
                # 不需要等待返回值
                sock.close()
        except Exception as e:
            LOG.exception(e)
            raise RPCFailedException

