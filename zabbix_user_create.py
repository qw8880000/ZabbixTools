# -*- coding: utf-8 -*-
import sys
import os
import logging
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

#
# logger configuration
# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=logging.WARNING)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)

def open_pyzabbix_debug():
    #
    # configure the logger level of pyzabbix 
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

def usergroups_get(group_names):
    """ 获取usergroup
    Args:
        group_names: group name 字符串，以逗号分隔
    Returns:
        usergroup数组
    """
    usergroups = []

    for group_name in group_names.split(','):
        for group in zapi.usergroup.get(output='extend', search={'name': group_name}):
            usergroups.append({'usrgrpid': group['usrgrpid']})
    else:
        return usergroups

def user_create(alias, name, usrgrps):
    return zapi.user.create(alias=alias,
            name=name,
            usrgrps=usrgrps,
            passwd='123456',
            lang='zh_CN')

if __name__ == "__main__":
    #
    # xlrd
    workbook = xlrd.open_workbook('./zabbix_user_create.xlsx')
    sheet = workbook.sheet_by_name('user')

    #  open_pyzabbix_debug()

    #
    # about zabbix
    zapi = ZabbixAPI('http://192.25.107.14:8000/')
    zapi.login('Admin', 'zabbix')

    try:
        for rindex in range(1, sheet.nrows):
            alias = sheet.cell_value(rindex, 0)
            name = sheet.cell_value(rindex, 1)
            usrgrps = usergroups_get(sheet.cell_value(rindex, 2))

            user_create(alias=alias, name=name, usrgrps=usrgrps)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

