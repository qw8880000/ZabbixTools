# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
import xlwt
import socket
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

if __name__ == "__main__":

    zabbix_server = "http://198.25.100.36:8181"
    zabbix_user = "Admin"
    zabbix_password = "zabbix"

    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("user")

    try:
        hosts = zapi.host.get(filter={"status":"0"})
        for index,host in enumerate(hosts):
            if is_port_opened(host["host"], 10050) == True:
                status = "open"
            else:
                status = "close"

            sheet.write(index, 0, host["host"])
            sheet.write(index, 1, status)
                
    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

    workbook.save("./host_port.xlsx")

