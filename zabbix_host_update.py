# -*- coding: utf-8 -*-
import sys
import os
import logging
import argparse
import xlrd
from pyzabbix import ZabbixAPI, ZabbixAPIException

import myutils

logger = myutils.init_logger()

g_proxy_dict = {}
g_group_dict = {}
g_template_dict = {}

#
# Get proxy_id by proxy name
#
def get_proxy_id(proxy):
    if proxy in g_proxy_dict:
        return g_proxy_dict[proxy]
    else:
        proxys = zapi.proxy.get(filter={"host": proxy})
        if len(proxys) == 0:
            return None

        proxy_id = proxys[0]["proxyid"]
        g_proxy_dict[proxy] = proxy_id
        return proxy_id

#
# Get group_id by group name
#
def get_group_id(group):
    if group in g_group_dict:
        return g_group_dict[group]
    else:
        hostgroups = zapi.hostgroup.get(filter={"name": group})
        if len(hostgroups) == 0:
            return None

        group_id = hostgroups[0]["groupid"]
        g_group_dict[group] = group_id
        return group_id

#
# Get template_id by template name
#
def get_template_id(template):
    if template in g_template_dict:
        return g_template_dict[template]
    else:
        templates = zapi.template.get(filter={"host": template})
        if len(templates) == 0:
            return None

        template_id = templates[0]["templateid"]
        g_template_dict[template] = template_id
        return template_id


def add_templateid_to_host(zapi, hostid, new_template_id):
    templateids = []
    templates_old = zapi.template.get(hostids=hostid)

    for temp in templates_old:
        templateids.append({ "templateid": temp["templateid"] })

    templateids.append({ "templateid": new_template_id})
    
    return templateids

def add_groupid_to_host(host, new_group_id):
    groupids = []

    for g in host["groups"]:
        groupids.append({"groupid": g["groupid"]})

    groupids.append({"groupid": new_group_id})
    
    return groupids

def del_groupid_from_host(host, group_id):
    groupids = []

    for g in host["groups"]:
        if g["groupid"] == group_id:
            continue
        else:
            groupids.append({"groupid": g["groupid"]})

    return groupids

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
    parser.add_argument("--add-template", dest="add_template", help="", action="store_true")
    parser.add_argument("--del-template", dest="del_template", help="", action="store_true")
    parser.add_argument("--add-group", dest="add_group", help="", action="store_true")
    parser.add_argument("--del-group", dest="del_group", help="", action="store_true")
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
    del_template = args.del_template
    add_group = args.add_group
    del_group = args.del_group
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

    for rindex in range(1, sheet.nrows):
        host_name = myutils.xlrd_cell_value_getstr(sheet, rindex, 0)
        host_sofeware = myutils.xlrd_cell_value_getstr(sheet, rindex, 1)
        host_system = myutils.xlrd_cell_value_getstr(sheet, rindex, 2)
        host_ip = myutils.xlrd_cell_value_getstr(sheet, rindex, 3)
        host_proxy = myutils.xlrd_cell_value_getstr(sheet, rindex, 4)
        host_group = myutils.xlrd_cell_value_getstr(sheet, rindex, 5)
        host_template = myutils.xlrd_cell_value_getstr(sheet, rindex, 6)

        host_visible_name = u"{0}-{1}".format(host_sofeware , host_ip)

        if host_name == "":
            logger.info("====> host_name is empty.index %d", rindex)
            continue

        try:

            hosts = zapi.host.get(filter={"host": host_name}, selectGroups="extend")
            if len(hosts) == 0:
                logger.info("====> host does not exist, host name: %s", host_name)
                continue

            current_host = hosts[0]
            hostid = current_host["hostid"]
            params = { "hostid": hostid }

            # name
            if update_name == True:
                params["name"] = host_visible_name

            # host group
            if add_group == True:
                group_id = get_group_id(host_group)
                if group_id != None:
                    params["groups"] = add_groupid_to_host(current_host, group_id)
                else:
                    logger.warning("Can't find hostgroup %s.", host_group)

            # host group del
            if del_group == True:
                group_id = get_group_id(host_group)
                if group_id != None:
                    params["groups"] = del_groupid_from_host(current_host, group_id)
                else:
                    logger.warning("Can't find hostgroup %s.", host_group)

            # proxy
            if update_proxy == True:
                proxy_id = get_proxy_id(host_proxy)
                if proxy_id != None:
                    params["proxy_hostid"] = proxy_id
                else:
                    logger.warning("Can't find proxy %s.", host_proxy)

            # template add
            if add_template == True:
                template_id = get_template_id(host_template)
                if template_id != None:
                    params["templates"] = add_templateid_to_host(zapi, hostid, template_id)
                else:
                    logger.warning("Can't find template %s.", host_template)


            # template delete
            if del_template != None:
                template_id = get_template_id(host_template)
                if template_id != None:
                    params["templates_clear"] = [{"templateid": template_id}]
                else:
                    logger.warning("Can't find template %s.", host_template)

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

