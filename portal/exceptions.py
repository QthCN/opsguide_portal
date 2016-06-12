# -*- coding: utf-8 -*-


class AuthFailedException(Exception):
    """认证失败"""


class RPCFailedException(Exception):
    """和Controller交互出错"""


class RPCContentException(Exception):
    """Controller处理消息异常"""
