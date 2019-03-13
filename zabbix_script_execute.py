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
    parser.add_argument("--script", dest="script", help="The script.", required=True)
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password
    zabbix_script = args.script

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
        scripts = zapi.script.get(filter={"name": zabbix_script})
        if len(scripts) == 0:
            logger.error("script [%s] does not exist.", zabbix_script)
            sys.exit()

        scriptid = scripts[0]["scriptid"]

        for rindex in range(1, sheet.nrows):
            host_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
            host_visible_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
            host_system = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)
            host_ip = myutils.xlrd_cell_value_getstr(sheet, rindex, 3)

            if host_name == "":
                continue

            # 创建主机
            hosts = zapi.host.get(filter={"host": host_name})
            if len(hosts) == 0:
                logger.info("xxxx host [%s] does not exist.", host_name)
            else:
                host_id = hosts[0]["hostid"]
                ret = zapi.script.execute(
                        hostid=host_id,
                        scriptid=scriptid
                        )

                logger.info("===> host [%s],response=%s,value=%s", host_name, ret["response"], ret["value"])


    except ZabbixAPIException as e:
        logger.info("00000000 host [%s] some error", host_name)
        logger.error(e)

