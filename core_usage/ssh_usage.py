#!/usr/bin/env python3
# -*- coding:utf8 -*-

import paramiko


class SSHConnect(object):
    '''
    ssh 跳板连接工具类
    '''

    def __init__(self, host, port, username, pkey_path, *args, **kwargs):
        '''
        初始化类属性
        '''
        self.host = host
        self.port = port     
        self.sock = self.host, self.port
        self.username = username
        self.pkey_path = pkey_path
        self.pkey = paramiko.RSAKey.from_private_key_file(self.pkey_path)
        self._transport = None
        self._sftp = None
        self._client = None
        self._connect()
        

    def _connect(self, *args, **kwargs):
        '''
        建立ssh连接传输
        '''
        transport = paramiko.Transport(sock=self.sock)
        transport.connect(username=self.username, pkey=self.pkey)
        self._transport = transport


    def download(self, remotepath, localpath, *args, **kwargs):
        '''
        sftp 下载功能
        '''
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)

        try:   
            self._sftp.get(remotepath=remotepath, localpath=localpath)
        except remotepath is None:
            print("remotepath is required!")
        except localpath is None:
            print("localpath is required!")
        except Exception as e:
            print(f"Error: {e}.")



    def upload(self, localpath, remotepath, *args, **kwargs):
        '''
        sfp 上传功能
        '''
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)

        try:
            self._sftp.put(localpath=localpath ,remotepath=remotepath)        
        except remotepath is None:
            print("remotepath is required!")
        except localpath is None:
            print("localpath is required!")
        except Exception as e:
            print(f"Error: {e}.")


    
    def exec_command(self, command, *args, **kwargs):
        '''
        执行命令行命令
        '''     
        if self._client is None:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._client._transport = self._transport

        
        stdin , stdout, stderr = self._client.exec_command(command)


        output = stdout.read().decode('utf-8')
        if len(output) > 0:
            return output.strip()
            

        error = stderr.read().decode('utf-8')
        if len(error) > 0:
            return error.strip()




# if __name__ == '__main__':

#     host      = '120.26.161.148'
#     port      = 36022
#     username  = 'uniondrug'
#     pkey_path = '/Users/shenlei/.ssh/id_rsa'

#     ssh_obj = SSHConnect(host, port, username, pkey_path)

#     ssh_obj.exec_command("hostname")