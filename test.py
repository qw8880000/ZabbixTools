# -*- coding: utf-8 -*-
import sys
import os
import logging
import xlwt
from pyzabbix import ZabbixAPI

#
# logger configuration
stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(logging.Formatter('%(asctime)s-%(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S'))
logger = logging.getLogger(__name__)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)

def open_pyzabbix_debug():
    #
    # configure the logger level of pyzabbix 
    stream = logging.StreamHandler(sys.stdout)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    #
    # about zabbix
    zapi = ZabbixAPI('http://198.25.100.36:8181/')
    zapi.login('Admin', 'zabbix')

    logger.info('test')

    open_pyzabbix_debug()
    zapi.user.get(filter={'alias': 'guest'})

