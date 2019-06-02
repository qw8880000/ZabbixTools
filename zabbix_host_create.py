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
            host_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
            host_sofeware = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
            host_system = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)
            host_ip = myutils.xlrd_cell_value_getstr(sheet, rindex, 3)
            host_proxy = myutils.xlrd_cell_value_getstr(sheet, rindex, 4)
            host_group = myutils.xlrd_cell_value_getstr(sheet, rindex, 5)

            if host_name == "":
                continue

            hostgroups = zapi.hostgroup.get(filter={"name": host_group})
            if len(hostgroups) == 0:
                logger.warning("Can't find hostgroup %s.", host_group)
                continue

            gid = hostgroups[0]["groupid"]

            host_visible_name = u"{0}-{1}".format(host_sofeware, host_ip)
            
            # 创建主机
            host_id = None
            hosts = zapi.host.get(filter={"host": host_name})
            if len(hosts) == 0:
                ret = zapi.host.create(
                        host=host_name,
                        name=host_visible_name,
                        interfaces={
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": host_ip,
                            "dns": "",
                            "port": "10050"
                            },
                        groups=[{"groupid": gid}],
                        )
                host_id = ret["hostids"][0]
                logger.info("====> create success, host name: %s, host_id: %s", host_name, host_id)
            else:
                host_id = hosts[0]["hostid"]
                logger.info("==> already exist, host name: %s, host_id: %s", host_name, host_id)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

