#!/usr/bin/env python3
# -*- coding:utf8 -*-

'''
Notice: If you want to use psycopg2, you must install the postgresql first. pg_config is necessary.
for macOS X
1. brew install postgresql
2. PATH=$PATH:/usr/local/Cellar/postgresql/12.1/bin/
3. python -m pip install psycopg2
'''

import re
import psycopg2


class PostgreConnect(object):
    '''
    postgre 连接操作工具类
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
            return psycopg2.connect(host=self._host,
                                    port=self._port,
                                    user=self._user,
                                    password=self._pass,
                                    database=self._db)

        except Exception as e:
            print(f'Error: {e}.')


    def dql_fetchone(self, sql, *args, **kwargs):
        '''
        DQL 语句执行器，获取一条返回记录
        '''
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制

            # 使用cursor()方法获取操作游标
            with self.server.cursor() as cursor:
                
                cursor.execute(sql)  # 执行sql语句

            return cursor.fetchone() # 获取一条查询记录

        except Exception as e:
            print(f'Error: {e}.')



    def dql_fetchall(self, sql, *args, **kwargs):
        '''
        DQL 语句执行器，获取所有返回记录
        '''
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制

            # 使用cursor()方法获取操作游标
            with self.server.cursor() as cursor:
                
                cursor.execute(sql)  # 执行sql语句

            return cursor.fetchall() # 获取所有查询记录

        except Exception as e:
            print(f'Error: {e}.')


      
    def ddl_operator(self, sql, *args, **kwargs):
        '''
        DDL 语句执行器
        '''
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制

            # 使用cursor()方法获取操作游标
            with self.server.cursor() as cursor:
                
                cursor.execute(sql)  # 执行sql语句

                self.server.commit() # 手动commit

        except Exception as e:
            print(f'Error: {e}.')
            self.server.rollback()   # 如果发生错误则回滚




    def dml_operator(self, sql, *args, **kwargs):
        '''
        DML 语句执行器
        '''
        try:
            self._connect().ping(reconnect=True)    # 检查数据库连接，重连机制

            # 使用cursor()方法获取操作游标
            with self.server.cursor() as cursor:
                
                cursor.execute(sql)  # 执行sql语句

                self.server.commit() # 手动commit

        except Exception as e:
            print(f'Error: {e}.')
            self.server.rollback()   # 如果发生错误则回滚