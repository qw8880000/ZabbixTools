# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

def is_user_exist(user, users):
    for u in users:
        if user["alias"] == u["alias"]:
            return True
    else:
        return False
def get_user_exist(user, users):
    for u in users:
        if user["alias"] == u["alias"]:
            return u
    else:
        return None



def user_medias_get(usermedias):
    user_medias = []

    for media in usermedias:
        if media["mediatypeid"] == "4": # 邮件
            mid = "6"
        elif media["mediatypeid"] == "5": # 短信
            mid = "4"
        elif media["mediatypeid"] == "6": # 微信
            mid = "5"

        user_medias.append({
            "mediatypeid": mid,
            "sendto": media["sendto"]
            })

    return user_medias

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source-server", dest="source_server", help="The source zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-d", "--dest-server", dest="dest_server", help="The dest zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-u", "--user", dest="user", help="The zabbix user.", metavar="USER", required=True)
    parser.add_argument("-p", "--password", dest="password", help="The zabbix password.", metavar="PASSWORD", required=True)
    parser.add_argument("--gid", dest="gid", help="The usergroup id.", metavar="USERGROUP ID", required=True)
    args = parser.parse_args()

    zabbix_server_source = args.source_server
    zabbix_server_dest = args.dest_server
    zabbix_user = args.user
    zabbix_password = args.password
    zabbix_gid = args.gid

    #
    # about zabbix
    zapi_source = ZabbixAPI(zabbix_server_source)
    zapi_source.login(zabbix_user, zabbix_password)

    zapi_dest = ZabbixAPI(zabbix_server_dest)
    zapi_dest.login(zabbix_user, zabbix_password)

    try:
        users_source = zapi_source.user.get()
        users_dest = zapi_dest.user.get()

        mediatypes_dest = zapi_dest.mediatype.get()

        for user in users_source:
            if is_user_exist(user, users_dest) == True:

                usermedias = zapi_source.usermedia.get(userids=user["userid"])
                user1 = get_user_exist(user, users_dest)

                #  zapi_dest.user.update(
                        #  userid=user["userid"],
                        #  user_medias=user_medias_get(usermedias)
                        #  )
                zapi_dest.user.updatemedia(
                        users=[{"userid": user1["userid"]}],
                        medias=user_medias_get(usermedias)
                        )

                logger.info("xxxx %s is already exist", user["alias"])
            else:
                usermedias = zapi_source.usermedia.get(userids=user["userid"])

                zapi_dest.user.create(
                        alias=user["alias"],
                        name=user["name"],
                        usrgrps=[{"usrgrpid": zabbix_gid}],
                        type=user["type"],
                        user_medias=user_medias_get(usermedias),
                        passwd="123456",
                        lang=user["lang"]
                        )
                logger.info("====> %s create success", user["alias"])
    except ZabbixAPIException as e:
        logger.error(e)
        sys.exit()

