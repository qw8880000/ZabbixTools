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

def get_aplication_name(applications):
    name = u''
    for app in applications:
        name += u'{} '.format(app['name'])

    return name

def get_monitor_item_from_hosts(hosts):
    lines = []

    for host in hosts:
        # 过滤掉状态为禁用的主机
        if host['status'] != '0':
            continue

        # if host['host'] == '198.25.100.32':
        #    continue

        logger.info('hostip=%s, hostname=%s, hostid=%s', host['host'], host['name'], host['hostid'])
        next_host_flag = 1 

        # 根据hostid查找监控项
        for item in zapi.item.get(hostids=host['hostid'], monitored='True', sortfield='name', output='extend'):
            # 过滤掉从template继承来的监控项
            if item['templateid'] != '0':
                continue

            application_name = get_aplication_name(zapi.application.get(itemids=item['itemid']))

            logger.info('\t%s %s %s', item['name'], item['key_'], application_name)

            item_info = {'host': '', 'hostname': '', 'itemname': '', 'itemkey': '', 'application': ''}

            if next_host_flag == 1:
                item_info['host'] = host['host']
                item_info['hostname'] = host['name']
                next_host_flag = 0
            else:
                item_info['host'] = ''
                item_info['hostname'] = ''

            item_info['itemname'] = item['name']
            item_info['itemkey'] = item['key_']
            item_info['application'] = application_name

            lines.append(item_info)

    else:
        return lines


def get_monitor_item_from_hosts_and_itemname(hosts, itemname):
    lines = []

    for host in hosts:
        # 过滤掉状态为禁用的主机
        if host['status'] != '0':
            continue

        logger.info('hostip=%s, hostname=%s, hostid=%s', host['host'], host['name'], host['hostid'])
        next_host_flag = 1 

        # 根据hostid查找监控项
        for item in zapi.item.get(hostids=host['hostid'], search={'name': itemname}, monitored='True', sortfield='name', output='extend'):
            # 过滤掉从template继承来的监控项
            if item['templateid'] != '0':
                continue

            application_name = get_aplication_name(zapi.application.get(itemids=item['itemid']))

            logger.info('\t%s %s %s', item['name'], item['key_'], application_name)

            item_info = {'host': '', 'hostname': '', 'itemname': '', 'itemkey': '', 'application': ''}

            if next_host_flag == 1:
                item_info['host'] = host['host']
                item_info['hostname'] = host['name']
                next_host_flag = 0
            else:
                item_info['host'] = ''
                item_info['hostname'] = ''

            item_info['itemname'] = item['name']
            item_info['itemkey'] = item['key_']
            item_info['application'] = application_name

            lines.append(item_info)

    else:
        return lines

if __name__ == "__main__":
    #
    # xlrd
    software_name = u'数据仓库'
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet(software_name)

    #
    # about zabbix
    zapi = ZabbixAPI('http://198.25.100.36:8181/')
    zapi.login('Admin', 'zabbix')

    row = 0
    # 模糊查找名称为 search_name 的主机组
    for hostgroup in zapi.hostgroup.get(search={'name': [software_name]}, sortfield='name'):
        # 根据groupid查找主机
        hosts = zapi.host.get(groupids=hostgroup['groupid'])

        lines = get_monitor_item_from_hosts(hosts)
        for line in lines:
            sheet.write(row, 0, line['host'])
            sheet.write(row, 1, line['hostname'])
            sheet.write(row, 2, line['itemname'])
            sheet.write(row, 3, line['application'])
            sheet.write(row, 4, line['itemkey'])
            row += 1

    #
    # 公共跳转机
    common_host_ips = ('198.25.101.98', '198.25.100.40')
    common_hosts = []
    for host_ip in common_host_ips:
        for host in zapi.host.get(filter={'host': host_ip}):
            common_hosts.append(host)

    lines = get_monitor_item_from_hosts_and_itemname(common_hosts, software_name)
    for line in lines:
        sheet.write(row, 0, line['host'])
        sheet.write(row, 1, line['hostname'])
        sheet.write(row, 2, line['itemname'])
        sheet.write(row, 3, line['application'])
        sheet.write(row, 4, line['itemkey'])
        row += 1
    #
    # End
    tempdir = './.tmp'
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)

    filename = u'{0}/zabbix-{1}.xlsx'.format(tempdir, software_name)
    workbook.save(filename)

