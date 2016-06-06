# -*- coding: utf-8 -*-
import logging

from oslo_config import cfg
from oslo_log import log


CONF = cfg.CONF


FILE_OPTIONS = {
    'server': [
        cfg.StrOpt('host',
                   default='0.0.0.0',
                   help='Server listening address.'),
        cfg.IntOpt('port',
                   default=7788,
                   help='Server listening port.'),
        cfg.BoolOpt('debug',
                    default=True,
                    help='Run in debug mode.')
    ],
}


def setup_logging(project=""):
    log.setup(CONF, project)


def configure(conf=None, version=None, config_files=None,
              project="",
              pre_setup_logging_fn=lambda: None):
    if conf is None:
        conf = CONF

    for section in FILE_OPTIONS:
        for option in FILE_OPTIONS[section]:
            if section:
                conf.register_cli_opt(option, group=section)
            else:
                conf.register_cli_opt(option)

    set_default_for_default_log_levels()

    CONF(project=project, version=version,
         default_config_files=config_files)

    pre_setup_logging_fn()
    setup_logging(project=project)


def list_opts():
    """Return a list of oslo_config options available.

    The returned list includes all oslo_config options which are registered as
    the "FILE_OPTIONS" in wsgi_basic.common.config. This list will not include
    the options from the oslo-incubator library or any options registered
    dynamically at run time.

    Each object in the list is a two element tuple. The first element of
    each tuple is the name of the group under which the list of options in the
    second element will be registered. A group name of None corresponds to the
    [DEFAULT] group in config files.

    This function is also discoverable via the 'oslo_config.opts' entry point
    under the 'wsgi_basic.config.opts' namespace.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users by this library.

    :returns: a list of (group_name, opts) tuples
    """
    return list(FILE_OPTIONS.items())


def set_default_for_default_log_levels():
    extra_log_level_defaults = [
    ]

    log.register_options(CONF)
    CONF.set_default("default_log_levels",
                     CONF.default_log_levels + extra_log_level_defaults)
