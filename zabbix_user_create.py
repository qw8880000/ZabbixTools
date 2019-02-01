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

def usergroups_get(group_names):
    """ 获取usergroup
    Args:
        group_names: group name 字符串，以逗号分隔
    Returns:
        usergroup数组
    """
    usergroups = []

    for group_name in group_names.split(','):
        for group in zapi.usergroup.get(output='extend', search={'name': group_name}):
            usergroups.append({'usrgrpid': group['usrgrpid']})
    else:
        return usergroups

def usertype_get(usertype):
    if usertype == 'super admin':
        return 3
    elif usertype == 'admin':
        return 2
    else:
        return 1

def user_medias_get(wechat, phone, email):
    user_medias = []

    if wechat.strip() != '':
        user_medias.append({
            'mediatypeid': '1',
            'sendto': wechat
            })
    if phone.strip() != '':
        user_medias.append({
            'mediatypeid': '2',
            'sendto': phone
            })
    if email.strip() != '':
        user_medias.append({
            'mediatypeid': '3',
            'sendto': email
            })

    return user_medias

def user_create(alias, name, usrgrps, type, user_medias):
    return zapi.user.create(alias=alias,
            name=name,
            usrgrps=usrgrps,
            type=type,
            user_medias=user_medias,
            passwd='123456',
            lang='zh_CN')

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
    sheet = workbook.sheet_by_name('user')

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    try:
        for rindex in range(1, sheet.nrows):
            alias = xlrd_cell_value_getstr(sheet, rindex, 0)
            name = xlrd_cell_value_getstr(sheet, rindex, 1)
            usrgrps = usergroups_get(xlrd_cell_value_getstr(sheet, rindex, 2))
            usertype = usertype_get(xlrd_cell_value_getstr(sheet, rindex, 3))
            wechat = xlrd_cell_value_getstr(sheet, rindex, 4)
            phone = xlrd_cell_value_getstr(sheet, rindex, 5)
            email = xlrd_cell_value_getstr(sheet, rindex, 6)

            user_medias = user_medias_get(wechat, phone, email)

            # 判断用户是否已经存在
            users = zapi.user.get(filter={'alias': alias})
            if len(users) == 0:
                zapi.user.create(
                        alias=alias,
                        name=name,
                        usrgrps=usrgrps,
                        type=usertype,
                        user_medias=user_medias,
                        passwd='123456',
                        lang='zh_CN'
                        )
                logger.info('====> %s create success', alias)
            else:
                logger.info('xxxx %s is already exist', alias)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

