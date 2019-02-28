# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import json
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
    parser.add_argument("-m", "--method", dest="method", help="The zabbix method.", metavar="METHOD", required=True)
    parser.add_argument("-a", "--params", dest="params", help="The zabbix params.", metavar="PARAMS", action="append", required=True)
    args = parser.parse_args()

    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password
    zabbix_method = args.method

    zabbix_params = "{" + ",".join(args.params) + "}"

    print zabbix_params
    tmp = json.loads(zabbix_params)

    print tmp
    """
    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    try:
        ret = zapi.do_request(
                method=zabbix_method,
                params=zabbix_params
                )

        print ret
    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

    """
