# -*- coding: utf-8 -*-
import os
import sys

from portal.server.core import run


# If ../../portal/__init__.py exists, add ../../ to Python search path, so
# that it will override what happens to be installed in
# /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                   os.pardir,
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir,
                               'portal',
                               '__init__.py')):
    sys.path.insert(0, possible_topdir)


def main():
    run(possible_topdir)
