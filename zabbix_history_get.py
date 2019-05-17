# -*- coding: utf-8 -*-
import sys
import os
import re
import logging
import argparse
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", dest="server", help="The zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-u", "--user", dest="user", help="The zabbix user.", metavar="USER", required=True)
    parser.add_argument("-p", "--password", dest="password", help="The zabbix password.", metavar="PASSWORD", required=True)
    parser.add_argument("--name", dest="name", help="The item name.", required=True)
    parser.add_argument("--htype", dest="htype", help="The history type.", required=True)
    args = parser.parse_args()

    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password
    zabbix_item_name = args.name
    zabbix_history_type = args.htype

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    #  items = zapi.item.get(filter={"name": zabbix_item_name}, inherited="True")
    items = zapi.item.get(filter={"name": zabbix_item_name}, inherited="True", output=["itemid", "hostid"])
    if len(items) == 0:
        logger.error("item name [%s] does not exist.", zabbix_item_name)
        sys.exit(1)

    for item in items:
        try:
            historys = zapi.history.get(itemids=item["itemid"], history=int(zabbix_history_type), sortfield="clock", sortorder="DESC", limit=1)
            host = zapi.host.get(hostids=item["hostid"], output=["hostid", "host", "name", "status", "available"])[0]

            # 过滤未启用的主机
            if str(host["status"]) != "0":
                continue

            if len(historys) == 0:
                logger.info("===> host [%s][%s], value=%s", host["name"], host["host"], "null")
            else:
                #print host["host"]
                logger.info("===> host [%s][%s], value=%s", host["name"], host["host"], historys[0]["value"])
                #if re.search("Windows", historys[0]["value"]) != None:
                #    logger.info("===> host [%s][%s], value=%s", host["name"], host["host"], historys[0]["value"])

        except ZabbixAPIException as e:
            logger.info("------- item [%s] some error", item["itemid"])
            logger.error(e)

