# -*- coding: utf-8 -*-

from portal.exceptions import AuthFailedException


class AuthBase(object):

    def __init__(self):
        pass

    def get_token_by_auth(self, username, password):
        raise NotImplementedError

    def validate_token(self, token):
        raise NotImplementedError


class SimpleAuth(AuthBase):

    def __init__(self):
        self.__auth_info = dict(
            admin='password',
            user='password'
        )

    def get_token_by_auth(self, username, password):
        if self.__auth_info.get(username, '_NO_SUCH_PWD_') == password:
            return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + username
        else:
            raise AuthFailedException

    def validate_token(self, token):
        for k, v in self.__auth_info:
            if token == 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + k:
                return dict(username=k)
        raise AuthFailedException
