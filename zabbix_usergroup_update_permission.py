# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', help='The input file.', metavar='INPUT_FILE', required=True)
    parser.add_argument('-s', '--server', dest='server', help='The zabbix server.', metavar='ZABBIX_SERVER', required=True)
    parser.add_argument('-u', '--user', dest='user', help='The zabbix user.', metavar='USER', required=True)
    parser.add_argument('-p', '--password', dest='password', help='The zabbix password.', metavar='PASSWORD', required=True)
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password

    if not os.path.exists(input_file):
        logger.warning('The input file does not exist: %s', input_file)
        sys.exit(1)

    if not os.path.isfile(input_file):
        logger.warning('The input file is not a file: %s', input_file)
        sys.exit(1)

    #
    # xlrd
    workbook = xlrd.open_workbook(input_file)
    sheet = workbook.sheet_by_index(0)

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    usergroup_info = { 'name': '', 'rights': [] }

    try:
        for rindex in range(1, sheet.nrows):
            #
            # excel 表格中，一个name 可以对应多个主机群组的权限设置
            # 以下代码开始构造 usergroup_info，例如：
            # usergroup_info = {
            #         'name': 'usergroup-1',
            #         'rights': [
            #             {'permission': '2', 'id': '15'},
            #             {'permission': '2', 'id': '20'},
            #             {'permission': '3', 'id': '10'}
            #             ]
            #         }
            name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
            if name != '':
                usergroup_info['name'] = name

            hostgroup_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
            hostgroups = zapi.hostgroup.get(filter={'name': hostgroup_name})
            if len(hostgroups) == 0:
                logger.info('==> does not exist, hostgroup name: %s', hostgroup_name)
                continue

            permission = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)

            right = { 'permission': permission, 'id': hostgroups[0]['groupid'] }
            usergroup_info['rights'].append(right)

            if (myutils.xlrd_cell_value_getstr(sheet, rindex + 1, 0) == '') or (rindex + 1 != sheet.nrows):
                continue

            #
            # usergroup_info 构造完成后，开始更新 usergroup
            usergroups = zapi.usergroup.get(filter={'name': name})
            if len(usergroups) == 0:
                logger.info('==> does not exist, usergroup name: %s', name)
                continue

            usergroup_id = usergroups[0]['usrgrpid']

            # 更新 usergroup 的权限信息
            ret = zapi.usergroup.update(usrgrpid=usergroup_id, rights=usergroup_info['rights'])
            logger.info('====> update success, usergroup name: %s, hostgroup_name: %s', name, hostgroup_name)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

