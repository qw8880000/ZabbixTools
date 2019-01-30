# -*- coding: utf-8 -*-
import sys
import logging
import xlwt
from pyzabbix import ZabbixAPI

def open_pyzabbix_debug():
    #
    # configure the logger level of pyzabbix 
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)


if __name__ == "__main__":

    #
    # logger configuration
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.addHandler(stream)
    logger.setLevel(logging.DEBUG)

    #
    # xlrd
    software_name = 'esb'
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet(software_name)

    #
    # about zabbix
    zapi = ZabbixAPI('http://198.25.100.36:8181/')
    zapi.login('Admin', 'zabbix')

    row = 0
    # 模糊查找名称为 search_name 的主机组
    for hostgroup in zapi.hostgroup.get(search={'name': [software_name]}):
        # 根据groupid查找主机
        hosts = zapi.host.get(groupids=hostgroup['groupid'])

        for host in hosts:
            # 过滤掉状态为禁用的主机
            if host['status'] != '0':
                continue

            logger.info('hostip=%s, hostname=%s, hostid=%s', host['host'], host['name'], host['hostid'])
            next_host_flag = 1 


            # 根据hostid查找监控项
            for item in zapi.item.get(hostids=host['hostid']):
                # 过滤掉从template继承来的监控项
                if item['templateid'] != '0':
                    continue

                application_name = u''
                for app in zapi.application.get(itemids=item['itemid']):
                    application_name += u'{},'.format(app['name'])

                logger.info('\t%s %s %s', item['name'], item['key_'], application_name)

                if next_host_flag == 1:
                    sheet.write(row, 0, host['host'])
                    sheet.write(row, 1, host['name'])
                    next_host_flag = 0
                else:
                    sheet.write(row, 0, '')
                    sheet.write(row, 1, '')

                sheet.write(row, 2, item['name'])
                sheet.write(row, 3, application_name)
                sheet.write(row, 4, item['key_'])
                row += 1


    # 公共跳转机
    common_hosts = ['198.25.101.98', '198.25.100.40']
    for host_ip in common_hosts:
        # 根据名称模糊查找监控项
        items = zapi.item.get(host=host_ip,
                search={'name': [software_name]})

        for item in items:
            logger.info('%s', item['name'])


    workbook.save('./zabbix.xlsx')
