# -*- coding: utf-8 -*-

import datetime


def convert_unix_timestamp_to_datetime_str(ut):
    return datetime.datetime.fromtimestamp(
        int(ut)
    ).strftime('%Y-%m-%d %H:%M:%S')
