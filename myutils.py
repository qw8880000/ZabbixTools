# -*- coding: utf-8 -*-
import sys
import os
import logging

def init_logger():
    """logger设置
    """
    # logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=logging.WARNING)
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(logging.Formatter('%(asctime)s-%(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S'))
    logger = logging.getLogger(__name__)
    logger.addHandler(stream)
    logger.setLevel(logging.DEBUG)
    
    return logger

def open_pyzabbix_debug():
    """configure the logger level of pyzabbix
    """
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
        return cell_value.strip()

