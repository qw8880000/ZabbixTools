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
stream.setFormatter(logging.Formatter('%(asctime)s-%(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S'))
logger = logging.getLogger(__name__)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)

def open_pyzabbix_debug():
    #
    # configure the logger level of pyzabbix 
    stream = logging.StreamHandler(sys.stdout)
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

def usertype_get(usertype):
    if usertype == 'super admin':
        return 3
    elif usertype == 'admin':
        return 2
    else:
        return 1

def user_create(alias, name, usrgrps, type):
    return zapi.user.create(alias=alias,
            name=name,
            usrgrps=usrgrps,
            type=type,
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
            type = usertype_get(sheet.cell_value(rindex, 3))

            if len(zapi.user.get(filter={'alias': alias})) == 0:
                user_create(alias=alias, name=name, usrgrps=usrgrps, type=type)
                logger.info('====> %s create success', alias)
            else:
                logger.info('xxxx %s is already exist', alias)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

