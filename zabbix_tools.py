# -*- coding: utf-8 -*-
import sys
import logging
from pyzabbix import ZabbixAPI

if __name__ == "__main__":
    #
    # configure the logger level of pyzabbix 
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

    #
    # about zabbix
    zapi = ZabbixAPI('http://198.25.100.36:8181/')
    zapi.login('Admin', 'zabbix')

