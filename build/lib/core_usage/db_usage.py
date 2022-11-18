#!/usr/bin/env python3
# -*- coding:utf8 -*-

import re
import pymysql


class MySQLConnect(object):
    '''
    mysql 连接操作工具类
    '''


    def __init__(self, host, port, username, password, dbname, *args, **kwargs):
        '''
        初始化类属性
        '''
        self._host  = host
        self._port  = port
        self._user  = username
        self._pass  = password
        self._db    = dbname
        self.server = self._connect()


    def _connect(self, *args, **kwargs):
        '''
        建立数据连接传输
        '''
        try:
            return pymysql.connect(host=self._host, 
                                  port=self._port, 
                                  user=self._user, 
                                  password=self._pass,
                                  db=self._db,
                                  charset='utf8mb4')
    
        except Exception as e:
            print(f'Error: {e}.')


    def dql_fetchone(self, sql, *args, **kwargs):
        '''
        DQL 语句执行器, 获取一条返回记录
        '''

        try:
            # 使用cursor()方法获取操作游标
            with self.server.cursor() as cursor:
                
                cursor.execute(sql)  # 执行sql语句

            return cursor.fetchone() # 获取一条查询记录

        except Exception as e:
            print(f'Error: {e}.')




    def dql_fetchall(self, sql, *args, **kwargs):
        '''
        DQL 语句执行器, 获取所有返回记录
        '''
        # 获取数据库操作游标
        cursor = self.server.cursor()
    
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制
            
            cursor.execute(sql)      # 执行dql语句
            return cursor.fetchall() # 返回查询结果
                  
        except Exception as e:
            print(f'Error: {e}.')



    
    def ddl_operator(self, sql, *args, **kwargs):
        '''
        DDL 语句执行器
        '''
        # 获取数据库操作游标
        cursor = self.server.cursor()
    
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制
            
            cursor.execute(sql)      # 执行ddl语句
            
            self.server.commit()     # 手动commit
            
        except Exception as e:
            print(f'Error: {e}.')
            self.server.rollback()   # 如果发生错误则回滚





    def dml_operator(self, sql, *args, **kwargs):
        '''
        DML 语句执行器
        '''
        # 获取数据库操作游标
        cursor = self.server.cursor()
    
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制
            
            cursor.execute(sql)      # 执行dml语句
            
            self.server.commit()     # 手动commit
            
        except Exception as e:
            print(f'Error: {e}.')
            self.server.rollback()   # 如果发生错误则回滚





# if __name__ == '__main__':

#     host     = '192.168.3.133'
#     port     = 13306
#     username = 'root'
#     password = '9!XY!Lq9o4dH'
#     dbname   = 'devops_analysis_testing'

#     db_obj = MySQLConnect(host=host, port=port, username=username, password=password, dbname=dbname)