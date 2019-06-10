# zabbix-tools

# 安装

安装依赖：`pip install -r requirements.txt`

# 脚本介绍

## `zabbix_user_create.py` 批量创建用户 

命令示例：
`python zabbix_user_create.py -i "./zabbix_user.xlsx" -s "http://110.110.110.110/zabbix" -u Admin -p zabbix`

## 批量创建用户组 `zabbix_usergroup_create.py`

命令示例：
`python zabbix_usergroup_create.py -i "./zabbix_usergroup.xlsx" -s "http://110.110.110.110/zabbix" -u Admin -p zabbix`

## 批量更新用户组权限

命令示例：
`python zabbix_usergroup_update_permission.py -i "./zabbix_usergroup.xlsx" -s "http://110.110.110.110/zabbix" -u Admin -p zabbix`

## `zabbix_host_update.py` 用于主机信息更新

```
python zabbix_host_update.py -s "http://110.110.110.110/zabbix" -u "Admin" -p "zabbix" -i "./zabbix_host.xlsx" --update-group --update-proxy --update-name 
```
