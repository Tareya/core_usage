#!/usr/bin/env python3
# -*- coding:utf8 -*-

from core_usage.db_usage import MySQLConnect

class MySQLServer(MySQLConnect):
    '''
    数据库操作
    '''

    def check_project_exist(self, project_name, *args, **kwargs):
        '''
        检测项目是否已存在与项目信息表中
        '''
        try:
            if len(project_name) != 0:
                sql = f"SELECT 1 FROM `resource_project_info` WHERE `name`=\'{project_name}\';"   # 以项目名(唯一)为条件查询
                return self.dql_fetchone(sql)[0]
            else:
                raise ValueError('project_name field can not be empty')

        except Exception as e:
            print(f'Error: {e}.')
        

    
    def get_project_record(self, project_name, *args, **kwargs):
        '''
        获取指定项目的记录
        '''
        try:
            if len(project_name) != 0:
                sql = f"SELECT * FROM `resource_project_info` WHERE `name`=\'{project_name}\';"
                return self.dql_fetchall(sql)[0]
            else:
                raise ValueError('project_name field can not be empty')

        except Exception as e:
            print(f'Error: {e}.')



    def get_project_fields(self, project_name, fields, *args, **kwargs):
        '''
        获取指定项目记录的指定字段
        '''
        try:
            if len(project_name) != 0 and len(fields) != 0:
                sql = f"SELECT {fields} FROM `resource_project_info` WHERE `name`=\'{project_name}\';"
                return self.dql_fetchall(sql)[0]
            elif len(project_name) == 0:
                raise ValueError('project_name field can not be empty')
            else:
                raise ValueError("fields can not be empty, multiple fields should be like 'field1, filed2'")

        except Exception as e:
            print(f'Error: {e}.')
        

    



# if __name__ == '__main__':

#     host     = '192.168.3.133'
#     port     = 13306
#     username = 'root'
#     password = '9!XY!Lq9o4dH'
#     dbname   = 'devops_analysis_testing'


#     # sql = 'SELECT `name`,`language` FROM `devops_analysis_testing`.`resource_project_info` LIMIT 0,1000;'

#     project_name = 'backend.app'
#     fields       = 'name, language, port, domain'


#     my_obj = MySQLServer(host=host, port=port, username=username, password=password, dbname=dbname)
#     print(my_obj.get_project_fields(project_name, fields))