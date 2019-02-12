# zabbix-tools

# 批量创建用户 `zabbix_user_create.py`

命令示例：
`python zabbix_user_create.py -i './zabbix_user.xlsx' -s http://192.25.107.14:8000 -u Admin -p zabbix`

# 批量创建用户组 `zabbix_usergroup_create.py`

命令示例：
`python zabbix_usergroup_create.py -i './zabbix_usergroup.xlsx' -s http://192.25.107.14:8000 -u Admin -p zabbix`

# 批量更新用户组权限

命令示例：
`python zabbix_usergroup_update_permission.py -i './zabbix_usergroup.xlsx' -s http://192.25.107.14:8000 -u Admin -p zabbix`
