# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

def usergroups_get(group_names):
    """ 获取usergroup
    Args:
        group_names: group name 字符串，以逗号分隔
    Returns:
        usergroup数组
    """
    usergroups = []

    for group_name in group_names.split(","):
        for group in zapi.usergroup.get(output="extend", search={"name": group_name}):
            usergroups.append({"usrgrpid": group["usrgrpid"]})
    else:
        return usergroups

def usertype_get(usertype):
    if usertype == "super admin":
        return 3
    elif usertype == "admin":
        return 2
    else:
        return 1

def get_mediatypeid_by_description(mediatypes, description):
    """在mediatypes中查找description对应的mediatypeid
    """
    for m in mediatypes:
        if m["description"] == description:
            return m["mediatypeid"]
    else:
        return "-1"

def user_medias_get(wechat, phone, email):
    user_medias = []

    if wechat["sendto"].strip() != "":
        user_medias.append(wechat)
    if phone["sendto"].strip() != "":
        user_medias.append(phone)
    if email["sendto"].strip() != "":
        user_medias.append(email)

    return user_medias

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="The input file.", metavar="INPUT_FILE", required=True)
    parser.add_argument("-s", "--server", dest="server", help="The zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-u", "--user", dest="user", help="The zabbix user.", metavar="USER", required=True)
    parser.add_argument("-p", "--password", dest="password", help="The zabbix password.", metavar="PASSWORD", required=True)
    parser.add_argument("--update", dest="update", action="store_true", help="If user exist, then update")
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password
    is_update = args.update

    if not os.path.exists(input_file):
        logger.warning("The input file does not exist: %s", input_file)
        sys.exit(1)

    if not os.path.isfile(input_file):
        logger.warning("The input file is not a file: %s", input_file)
        sys.exit(1)

    #
    # xlrd
    workbook = xlrd.open_workbook(input_file)
    sheet = workbook.sheet_by_name("user")

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    try:
        mediatypes = zapi.mediatype.get()
        mediatype_wechat_id = get_mediatypeid_by_description(mediatypes, u'微信')
        mediatype_phone_id = get_mediatypeid_by_description(mediatypes, u'短信')
        mediatype_email_id = get_mediatypeid_by_description(mediatypes, u'邮件')

        for rindex in range(1, sheet.nrows):
            alias = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
            name = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
            usrgrps = usergroups_get(myutils.xlrd_cell_value_getstr(sheet, rindex, 2))
            usertype = usertype_get(myutils.xlrd_cell_value_getstr(sheet, rindex, 3))

            wechat = { "mediatypeid": mediatype_wechat_id, "sendto": myutils.xlrd_cell_value_getstr(sheet, rindex, 4) }
            phone = { "mediatypeid": mediatype_phone_id, "sendto": myutils.xlrd_cell_value_getstr(sheet, rindex, 5) }
            email = { "mediatypeid": mediatype_email_id, "sendto": myutils.xlrd_cell_value_getstr(sheet, rindex, 6) }

            user_medias = user_medias_get(wechat, phone, email)

            # 判断用户是否已经存在
            users = zapi.user.get(filter={"alias": alias})
            if len(users) == 0:
                zapi.user.create(
                        alias=alias,
                        name=name,
                        usrgrps=usrgrps,
                        type=usertype,
                        user_medias=user_medias,
                        passwd="123456",
                        lang="zh_CN"
                        )
                logger.info("====> %s create success", alias)
            else:
                if is_update == True:
                    userid = users[0]["userid"]
                    zapi.user.update(
                            userid=userid,
                            user_medias=user_medias
                            )
                    zapi.user.updatemedia(
                            users=[{"userid": userid}],
                            medias=user_medias
                            )
                    logger.info("----> %s update success", alias)
                else:
                    logger.info("xxxx %s is already exist", alias)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

