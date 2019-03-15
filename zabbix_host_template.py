# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

def add_templateid_to_host(zapi, hostid, new_template_id):
    templateids = []
    templates_old = zapi.template.get(hostids=hostid)

    for temp in templates_old:
        templateids.append({ "templateid": temp["templateid"] })

    templateids.append({ "templateid": new_template_id})
    
    return templateids

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

    for rindex in range(1, sheet.nrows):
        host_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
        host_visible_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
        host_system = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)
        host_ip = myutils.xlrd_cell_value_getstr(sheet, rindex, 3)
        host_proxy = myutils.xlrd_cell_value_getstr(sheet, rindex, 4)

        if host_name == "":
            continue

        try:
            hosts = zapi.host.get(filter={"host": host_name})
            if len(hosts) == 0:
                #  logger.info("xxxx> host does not exist, host name: %s", host_name)
                continue

            hostid = hosts[0]["hostid"]
            host_status = hosts[0]["status"]
            item_name = []

            items = zapi.item.get(hostids=hostid)
            for item in items:
                item_name.append(item["name"])

            item_num = len(items)
            if host_status == "0" and item_num > 2:
                logger.info("==> host name: %s, item num: %d, item: [%s]", host_name, item_num, ",".join(item_name))

            #  templates = zapi.template.get(hostids=hostid)
            #  logger.info("==> update success, host name: %s", host_name)
            #  for temp in templates:
                #  logger.info("\t template [%s][%s], status %s, available %s, name [%s]", temp["host"], temp["templateid"], temp["status"], temp["available"], temp["name"])

        except ZabbixAPIException as e:
            logger.error("some error happened.[%s]", host_name)
            logger.error(e)

