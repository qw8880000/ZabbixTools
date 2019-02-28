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
    parser.add_argument("-i", "--input", dest="input", help="The input file.", metavar="INPUT_FILE", required=True)
    parser.add_argument("-s", "--server", dest="server", help="The zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-u", "--user", dest="user", help="The zabbix user.", metavar="USER", required=True)
    parser.add_argument("-p", "--password", dest="password", help="The zabbix password.", metavar="PASSWORD", required=True)
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password

    if not os.path.exists(input_file):
        logger.warning("The input file does not exist: %s", input_file)
        sys.exit(1)

    if not os.path.isfile(input_file):
        logger.warning("The input file is not a file: %s", input_file)
        sys.exit(1)

    #
    # xlrd
    workbook = xlrd.open_workbook(input_file)
    sheet = workbook.sheet_by_index(0)

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    try:
        for rindex in range(1, sheet.nrows):
            name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)

            if name == "":
                continue

            # 创建用户组
            usergroup_id = None
            usergroups = zapi.usergroup.get(filter={"name": name})
            if len(usergroups) == 0:
                ret = zapi.usergroup.create(name=name)
                usergroup_id = ret["usrgrpids"][0]
                logger.info("====> create success, usergroup name: %s, usergroup_id: %s", name, usergroup_id)
            else:
                usergroup_id = usergroups[0]["usrgrpid"]
                logger.info("==> already exist, usergroup name: %s, usergroup_id: %s", name, usergroup_id)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

