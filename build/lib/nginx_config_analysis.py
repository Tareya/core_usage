#!/usr/bin/env python3
# -*- coding:utf8 -*-

import re
from core_usage.ssh_usage import SSHConnect

class NginxConfigAnalysis(SSHConnect):
    '''
    nginx 配置文件分析工具类
    '''

    def get_running_env(self):
        '''
        自动适配环境变量信息
        '''
        try:
            nginx_conf_root = '/data/conf/nginx/conf.d'

            if self.host.find('192.168.3.') !=-1:
                nginx_server_host = 't-nginx-01'
            elif self.host.find('172.16.0.') !=-1:
                nginx_server_host = 'r-nginx-02'
            elif self.host.find('172.16.') !=-1 and host.find('172.16.0.') ==-1:
                nginx_server_host = 'p-nginx-01'
                            
            return nginx_server_host, nginx_conf_root

        except Exception as e:
            print(f'Error: {e}.')
            



    def get_nginx_vhost(self, project_name, *args, **kwargs):
        '''
        获取nginx 虚拟主机配置内容
        '''
        try:
            nginx_server_host, nginx_conf_root = self.get_running_env()

            contents = self.exec_command(f"ansible {nginx_server_host} -m shell -a \"cat {nginx_conf_root}/*{project_name}.conf\"|grep -v 'rc='")
            
            if contents.find('UNREACHABLE') ==-1 and contents.find('FAILED') ==-1:
                return contents
            else:
                raise ValueError(contents)

        except Exception as e:
            print(f'Error: {e}.')



    def check_pod_exsits(self, contents, *args, **kwargs):
        '''
        判断项目是否已接入k8s:
            存在 :180 且不存在 #server 为已接入k8s项目
        '''  
        try:          
            if contents.find(':180') != -1 and contents.find('#server') == -1:
                return 1
            else:
                return contents

        except Exception as e:
            print(f'Error: {e}.')




    def get_project_vm_distribution(self, contents, *args, **kwargs):
        '''
        获取项目虚拟主机分布信息: 
            ip_list： 实例所在虚机ip列表, 其元素个数即为实例数量
        '''
        try:
            ip_list = re.findall(f'\s+server\s*(.*):', contents)

            return ip_list, len(ip_list)
    
        except Exception as e:
            print(f'Error: {e}.')




    def get_backend_port(self, contents, *args, **kwargs):
        '''
        获取后端项目端口、反向代理域名
        '''
        try:
            port_list = re.findall('upstream\s*srv(.+).+{', contents)[0].split()            

            return port_list

        except Exception as e:
            print(f'Error: {e}.')



    def get_backend_domain(self, contents, *args, **kwargs):
        '''
        获取后端项目端口、反向代理域名
        '''
        try:
            domain_list = re.findall('server_name\s*(.+);', contents)[0].split(" ")

            return domain_list

        except Exception as e:
            print(f'Error: {e}.')



    def get_frontend_domain(self, contents, *args, **kwargs):
        '''
        获取前端项目域名
        '''
        try:
            domain_list = re.findall('server_name\s*(.+);', contents)[0].split(" ")
    
            return domain_list
        
        except Exception as e:
            print(f'Error: {e}.')



    def get_project_language(self, project_name, *args, **kwargs):
        '''
        判断项目类型:
            后端端口 > 30000 为java项目
            后端端口 8001~10000 为php项目
            后端端口 6000~8000 为golang项目        
        '''
        try:
            contents = self.get_nginx_vhost(project_name)

            if contents.find('UNREACHABLE') ==-1 and contents.find('FAILED') ==-1 and contents.find('non-zero') ==-1:

                if contents.find('upstream srv') !=-1:
                    port = self.get_backend_port(contents)[0]

                    if int(port) >= 30000:
                        return 'java'
                    elif int(port) < 10000 and int(port) > 8000:
                        return 'php'
                    elif int(port) < 8000 and int(port) >= 6000:
                        return 'golang'

                elif contents.find('upstream') ==-1 and contents.find('dist') !=-1:
                    return 'frontend'  
                elif contents.find('server') ==-1:
                    raise ValueError("Project vhost not found.")
                else:
                    return 'fpm'
            elif contents.find('non-zero') !=-1:
                raise ValueError('Project Vhost Configuration not found.')
            else:
                raise ValueError(contents)
        except Exception as e:
            print(f'Error: {e}.')

    

    

# if __name__ == '__main__':

#     host         = '192.168.3.33'
#     port         = 60022
#     username     = 'uniondrug'
#     pkey_path    = '/Users/shenlei/.ssh/id_rsa'
#     project_name = 'outreach.partners.data.api'




#     ngca = NginxConfigAnalysis(host, port, username, pkey_path)
#     # contents = ngca.get_nginx_vhost(project_name)

#     project_language = ngca.get_project_language(project_name)
#     print(project_language)
    