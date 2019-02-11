# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

#
# logger configuration
# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=logging.WARNING)
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

def xlrd_cell_value_getstr(sheet, rowx, colx):
    """获取sheet某单元格的值，如果是数字类型，则转换成字符串类型
    """
    cell_value = sheet.cell_value(rowx, colx)
    if type(cell_value).__name__ == 'float':
        return str(int(cell_value))
    else:
        return cell_value

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', help='The input file.', metavar='INPUT_FILE', required=True)
    parser.add_argument('-s', '--server', dest='server', help='The zabbix server.', metavar='ZABBIX_SERVER', required=True)
    parser.add_argument('-u', '--user', dest='user', help='The zabbix user.', metavar='USER', required=True)
    parser.add_argument('-p', '--password', dest='password', help='The zabbix password.', metavar='PASSWORD', required=True)
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password

    if not os.path.exists(input_file):
        logger.warning('The input file does not exist: %s', input_file)
        sys.exit(1)

    if not os.path.isfile(input_file):
        logger.warning('The input file is not a file: %s', input_file)
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
            name = xlrd_cell_value_getstr(sheet, rindex, 0)

            # 判断用户是否已经存在
            usergroups = zapi.usergroup.get(filter={'name': name})
            if len(usergroups) == 0:
                zapi.usergroup.create(
                        name=name,
                        )
                logger.info('====> %s create success', name)
            else:
                logger.info('xxxx %s is already exist', name)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

