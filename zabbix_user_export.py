# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlwt
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

def usertype_get(usertype):
    if usertype == "3":
        return "super admin"
    elif usertype == "2":
        return "admin"
    else:
        return "guest"

def get_sendto_by_mediatypeid(medias, mediatypeid):
    for m in medias:
        if m["mediatypeid"] == mediatypeid:
            return m["sendto"]
    else:
        return ""

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", dest="output", help="The output file.", metavar="OUTPUT_FILE", required=True)
    parser.add_argument("-s", "--server", dest="server", help="The zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-u", "--user", dest="user", help="The zabbix user.", metavar="USER", required=True)
    parser.add_argument("-p", "--password", dest="password", help="The zabbix password.", metavar="PASSWORD", required=True)
    args = parser.parse_args()

    out_file = args.output
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password

    #
    # xlwt
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("user")
    header = [u"别名(alias)", u"用户名(name)", u"群组(groups)", u"用户类型(User type)", u"微信", u"手机", u"邮箱"]
    for index,value in enumerate(header):
        sheet.write(0, index, value)

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    try:

        mediatype_wechat_id = zapi.mediatype.get(filter={"description": u"微信"})[0]["mediatypeid"]
        mediatype_phone_id = zapi.mediatype.get(filter={"description": u"短信"})[0]["mediatypeid"]
        mediatype_email_id = zapi.mediatype.get(filter={"description": u"邮件"})[0]["mediatypeid"]

        all_users = zapi.user.get()
        for index,user in enumerate(all_users):
            alias = user["alias"]
            name = user["name"]
            usertype = usertype_get(user["type"])

            usergroup = "Guests"

            user_medias = zapi.usermedia.get(userids=user["userid"])
            wechat = get_sendto_by_mediatypeid(user_medias, mediatype_wechat_id)
            phone = get_sendto_by_mediatypeid(user_medias, mediatype_phone_id)
            email = get_sendto_by_mediatypeid(user_medias, mediatype_email_id)

            sheet.write(index+1, 0, alias)
            sheet.write(index+1, 1, name)
            sheet.write(index+1, 2, usergroup)
            sheet.write(index+1, 3, usertype)
            sheet.write(index+1, 4, wechat)
            sheet.write(index+1, 5, phone)
            sheet.write(index+1, 6, email)

    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

    workbook.save(out_file)

