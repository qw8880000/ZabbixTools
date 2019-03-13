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
    parser.add_argument("--update-interface", dest="update_interface", help="", action="store_true")
    parser.add_argument("--update-template", dest="update_template", help="", action="store_true")
    parser.add_argument("--update-proxy", dest="update_proxy", help="", action="store_true")
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password
    update_interface = args.update_interface
    update_template = args.update_template
    update_proxy = args.update_proxy

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

    for rindex in range(1, sheet.nrows):
        host_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
        host_visible_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
        host_system = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)
        host_ip = myutils.xlrd_cell_value_getstr(sheet, rindex, 3)
        #  host_template = myutils.xlrd_cell_value_getstr(sheet, rindex, 4)
        host_template = "Template XYZQ Get System Info"
        host_proxy = myutils.xlrd_cell_value_getstr(sheet, rindex, 5)

        if host_name == "":
            continue

        try:
            params = {}

            # proxy
            if update_proxy == True:
                proxys = zapi.proxy.get(filter={"host": host_proxy})
                if len(proxys) != 0:
                    params["proxy_hostid"] = proxys[0]["proxyid"]

            # template
            if update_template == True:
                templates = zapi.template.get(filter={ "host": host_template.split(",") })
                if len(templates) > 0:
                    params["templates"] = []
                    for temp in templates:
                        params["templates"].append({ "templateid": temp["templateid"] }),

            # interface
            if update_interface == True:
                params["interfaces"] = {
                                "type": 1,
                                "main": 1,
                                "useip": 1,
                                "ip": host_ip,
                                "dns": "",
                                "port": "10050"
                                }

            hosts = zapi.host.get(filter={"host": host_name})
            if len(hosts) == 0:
                logger.info("====> host does not exist, host name: %s", host_name)
            else:
                hostid = hosts[0]["hostid"]
                params["hostid"] = hostid
                zapi.do_request(
                        method="host.update",
                        params=params
                        )
                logger.info("==> update success, host name: %s", host_name)

        except ZabbixAPIException as e:
            logger.error("some error happened.[%s]", host_name)
            logger.error(e)

