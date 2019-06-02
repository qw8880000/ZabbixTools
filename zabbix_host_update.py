# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

def add_templateid_to_host(zapi, hostid, new_template_id):
    templateids = []
    templates_old = zapi.template.get(hostids=hostid)

    for temp in templates_old:
        templateids.append({ "templateid": temp["templateid"] })

    templateids.append({ "templateid": new_template_id})
    
    return templateids

if __name__ == "__main__":
    #
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="The input file.", metavar="INPUT_FILE", required=True)
    parser.add_argument("-s", "--server", dest="server", help="The zabbix server.", metavar="ZABBIX_SERVER", required=True)
    parser.add_argument("-u", "--user", dest="user", help="The zabbix user.", metavar="USER", required=True)
    parser.add_argument("-p", "--password", dest="password", help="The zabbix password.", metavar="PASSWORD", required=True)
    parser.add_argument("--update-interface", dest="update_interface", help="", action="store_true")
    parser.add_argument("--update-proxy", dest="update_proxy", help="", action="store_true")
    parser.add_argument("--add-template", dest="add_template", help="")
    parser.add_argument("--delete-template", dest="delete_template", help="")
    parser.add_argument("--update-group", dest="update_group", help="", action="store_true")
    parser.add_argument("--update-name", dest="update_name", help="", action="store_true")
    parser.add_argument("--update-status", dest="update_status", help="", action="store_true")
    args = parser.parse_args()

    input_file = args.input
    zabbix_server = args.server
    zabbix_user = args.user
    zabbix_password = args.password
    update_interface = args.update_interface
    update_proxy = args.update_proxy
    add_template = args.add_template
    delete_template = args.delete_template
    update_group = args.update_group
    update_name = args.update_name
    update_status = args.update_status

    if not os.path.exists(input_file):
        logger.warning("The input file does not exist: %s", input_file)
        sys.exit(1)

    if not os.path.isfile(input_file):
        logger.warning("The input file is not a file: %s", input_file)
        sys.exit(1)

    #
    # xlrd
    workbook = xlrd.open_workbook(input_file)
    sheet = workbook.sheet_by_index(0)

    #
    # about zabbix
    zapi = ZabbixAPI(zabbix_server)
    zapi.login(zabbix_user, zabbix_password)

    if add_template != None:
        if add_template == "":
            logger.warning("Template is empty.")
            sys.exit(1)

        templates = zapi.template.get(filter={"host": add_template})
        if len(templates) == 0:
            logger.warning("Can't find template [%s] to add", add_template)
            sys.exit(1)
        else:
            templateid_add = templates[0]["templateid"]
            logger.info("the template [%s][%s] to add", add_template, templateid_add)
    elif delete_template != None:
        if delete_template == "":
            logger.warning("Template is empty.")
            sys.exit(1)

        templates = zapi.template.get(filter={"host": delete_template})
        if len(templates) == 0:
            logger.warning("Can't find template [%s] to delete", delete_template)
            sys.exit(1)
        else:
            templateid_delete = templates[0]["templateid"]
            logger.info("the template [%s][%s] to delete", delete_template, templateid_delete)

    for rindex in range(1, sheet.nrows):
        host_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
        host_sofeware = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
        host_system = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)
        host_ip = myutils.xlrd_cell_value_getstr(sheet, rindex, 3)
        host_proxy = myutils.xlrd_cell_value_getstr(sheet, rindex, 4)
        host_group = myutils.xlrd_cell_value_getstr(sheet, rindex, 5)

        host_visible_name = u"{0}-{1}".format(host_sofeware , host_ip)

        if host_name == "":
            continue

        try:

            hosts = zapi.host.get(filter={"host": host_name})
            if len(hosts) == 0:
                logger.info("====> host does not exist, host name: %s", host_name)
                continue

            hostid = hosts[0]["hostid"]
            params = { "hostid": hostid }

            # name
            if update_name == True:
                params["name"] = host_visible_name

            # host group
            if update_group == True:
                hostgroups = zapi.hostgroup.get(filter={"name": host_group})
                if len(hostgroups) == 0:
                    logger.warning("Can't find hostgroup %s.", host_group)
                else:
                    gid = hostgroups[0]["groupid"]
                    params["groups"] = [{"groupid": gid}]

            # proxy
            if update_proxy == True:
                proxys = zapi.proxy.get(filter={"host": host_proxy})
                if len(proxys) != 0:
                    params["proxy_hostid"] = proxys[0]["proxyid"]

            # template add
            if add_template != None:
                templateids = add_templateid_to_host(zapi, hostid, templateid_add)
                if len(templateids) > 0:
                    params["templates"] = templateids

            # template delete
            if delete_template != None:
                params["templates_clear"] = [{"templateid": templateid_delete}]

            # status
            if update_status == True:
                params["status"] = 0

            # interface
            if update_interface == True:
                params["interfaces"] = {
                                "type": 1,
                                "main": 1,
                                "useip": 1,
                                "ip": host_ip,
                                "dns": "",
                                "port": "10050"
                                }

            # update
            zapi.do_request(
                    method="host.update",
                    params=params
                    )
            logger.info("==> update success, host name: %s", host_name)

        except ZabbixAPIException as e:
            logger.error("some error happened.[%s]", host_name)
            logger.error(e)

