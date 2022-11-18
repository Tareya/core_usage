#!/usr/bin/env python
#coding=utf-8

# 阿里云api 核心类
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException

# 阿里云api 通用方法类
from aliyunsdkcore.request import CommonRequest 


class AliyunConnect(object):
    '''
    阿里云 API 调用连接方法类
    '''

    def __init__(self, *args, **kwargs):
        '''
        初始化类属性
        '''
        self.accessKeyId  = 'LTAI4FkeRPyPu7kEY8EPMTdv'
        self.accessSecret = 'UDdpw9F0YqOA0eyoKU71bsVHaIscN6'
        self.RegionId     = 'cn-hangzhou'
        self.client       = self._connect()



    def _connect(self, *args, **kwargs):
        '''
        建立阿里云连接
        '''
        try:
            return AcsClient(self.accessKeyId, self.accessSecret, self.RegionId)

        except Exception as e:
            print(f'Error: {e}.')


    
    