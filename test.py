# -*- coding: utf-8 -*-
import sys
import os
import logging
import xlwt
from pyzabbix import ZabbixAPI

#
# logger configuration
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)

def open_pyzabbix_debug():
    #
    # configure the logger level of pyzabbix 
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    #
    # about zabbix
    zapi = ZabbixAPI('http://198.25.100.36:8181/')
    zapi.login('Admin', 'zabbix')

    open_pyzabbix_debug()
    zapi.host.get(filter={'host': '198.25.101.98'})

