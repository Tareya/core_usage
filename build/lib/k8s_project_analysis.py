#!/usr/bin/env python3
# -*- coding:utf8 -*-

import re, os
from core_usage.ssh_usage import SSHConnect


class K8SProjectAnalysis(SSHConnect):
    '''
    k8s 接入项目分析工具类
    '''


    def get_running_env(self, *args, **kwargs):
        '''
        获取运行环境
        '''
        try:
            helm_config_root = '/data/apps'

            if self.host.find('192.168.3.') !=-1:
                k8s_master_host = 't-master-01'
                running_env     = 'testing'

            elif self.host.find('172.16.0.') !=-1:
                k8s_master_host = 'r-master-01'
                running_env     = 'release'

            elif self.host.find('172.16.') !=-1 and self.host.find('172.16.0.') == -1:
                k8s_master_host = 'p-master-01'
                running_env     = 'production'
            
            return running_env, k8s_master_host, helm_config_root
  
        except Exception as e:
            print(f'Error: {e}.')


    
    def replace_project_name(self, project_name, *args, **kwargs):
        '''
        替换项目名称，如果项目名称中存在 . 则全部替换成 - (k8s 不识别 .)
        '''
        try:
            if project_name.find('.') !=-1:
                return project_name.replace('.', '-')
            else:
                return project_name

        except Exception as e:
            print(f'Error: {e}.')




    def get_helm_config_path(self, project_name, *args, **kwargs):
        '''
        根据项目的语言类型获取helm配置路径
        '''
        try:
            running_env, k8s_master_host, helm_config_root = self.get_running_env()

            alias_name = self.replace_project_name(project_name)
            contents   = self.exec_command(f"ansible {k8s_master_host} -m shell -a \"find {helm_config_root} -type d -name '{alias_name}'\"|grep -v 'rc='")

            if contents.find('UNREACHABLE') ==-1 and contents.find('FAILED') ==-1 and len(contents) != 0:
                return contents
            elif len(contents) == 0:
                raise ValueError('Project Helm Template not found.')
            else:
                raise ValueError(contents)
        
        except Exception as e:
            print(f'Error: {e}.')




    def get_project_helm_temp(self, project_name, *args, **kwargs):
        '''
        获取项目helm模版kv配置
        '''
        try:
            running_env, k8s_master_host, helm_config_root = self.get_running_env()

            helm_path = self.get_helm_config_path(project_name)    
            contents = self.exec_command(f"ansible {k8s_master_host} -m shell -a \"cat {helm_path}/values.yaml\"|grep -v 'rc='")

            if contents.find('UNREACHABLE') ==-1 and contents.find('FAILED') ==-1:
                return contents
            else:
                raise ValueError(contents)

        except Exception as e:
            print(f'Error: {e}.')




    def get_project_namespace(self, project_name, *args, **kwargs):
        '''
        根据helm模版获取项目namespace
        '''
        try:
            running_env, k8s_master_host, helm_config_root = self.get_running_env()

            contents = self.exec_command(f"ansible {k8s_master_host} -m shell -a \"kubectl get pod -A | grep {project_name}\"|grep -v 'rc='")

            if contents.find('UNREACHABLE') ==-1 and contents.find('FAILED') ==-1 and contents.find('non-zero') ==-1:
                namespace = re.findall(f'(.+)\s+{project_name}.*', contents)[0].strip('')
                return namespace
            elif contents.find('non-zero') !=-1:
                raise ValueError('Project pod not found.')
            else:
                raise ValueError(contents)

        except Exception as e:
            print(f'Error: {e}.')




    def get_project_replicacount(self, contents, *args, **kwargs):
        '''
        根据helm模版获取预分配的rc数量
        '''
        try:
            rc_list = re.findall('\s*replicaCount:\s*(.+)', contents)
            
            if len(rc_list) == 1:
                return rc_list[0]
            else:
                raise ValueError('Error: plural replicaCount fields exist.')

        except Exception as e:
            print(f'Error: {e}.')

        

    def get_project_repository(self, contents, *args, **kwargs):
        '''
        根据helm模版获取项目镜像地址
        '''
        try:
            repository_list = re.findall('\s*repository:\s*(.+)', contents)

            if len(repository_list) == 1:
                return repository_list[0]
            else:
                raise ValueError('Error: plural repository fields exist.')
    
        except Exception as e:
            print(f'Error: {e}.')        


   
    def get_project_resource_spec(self, contents, *args, **kwargs):
        '''
        根据helm模版获取项目资源模版
        '''
        try:
            spec_list = re.findall('\s+limits:\n\s+memory:\s+(.+)\n\s+cpu:\s+(.+)', contents)

            if len(spec_list) == 1:
                memory, cpu = spec_list[0]
                return '{} {}'.format(cpu.replace('"',''), memory.replace('"', ''))           
            else:
                raise ValueError('Error: plural limit resource fields exist.')

        except Exception as e:
            print(f'Error: {e}.')




    def get_project_runtime(self, project_name, *args, **kwargs):
        '''
        获取项目运行状态信息
        '''
        try:
            running_env, k8s_master_host, helm_config_root = self.get_running_env()

            alias_name    = self.replace_project_name(project_name)
            namespace     = self.get_project_namespace(project_name)
            contents      = self.exec_command(f"ansible {k8s_master_host} -m shell -a \"kubectl get pod -n {namespace} -o wide|grep {alias_name}\"|grep -v 'rc='")

            return contents    

        except Exception as e:
            print(f'Error: {e}.')




    def get_project_pod_list(self, contents, *args, **kwargs):
        '''
        获取项目pod列表
        '''
        try:
            pod_list = []
            pods = re.findall('(.*)\s+\d/\d.*', contents)

            for pod in pods:
                pod_list.append(pod.split()[0])

            return pod_list

        except Exception as e:
            print(f'Error: {e}.')


    
    def get_pod_distribution(self, contents, *args, **kwargs):
        '''
        获取项目pod分布信息
        '''
        try:
            node_list = []
            nodes = re.findall('.*\d/\d.*\d+\s+.*\.\d+\s+(.+)\s+\<.*\<', contents)

            for node in nodes:
                node_list.append(node.split()[0])

            return node_list, len(node_list)

        except Exception as e:
            print(f'Error: {e}.')




    def get_pod_detail_yaml(self, pod_name, *args, **kwargs):
        '''
        获得pod详情yaml
        '''
        try:
            running_env, k8s_master_host, helm_config_root = self.get_running_env()

            project_name = re.findall('(.+)-\S{10}-\S{5}', pod_name)[0]
            namespace  = self.get_project_namespace(project_name)
            contents   = self.exec_command(f"ansible {k8s_master_host} -m shell -a \"kubectl describe pod -n {namespace} {pod_name}\"|grep -v 'rc='")

            return contents

        except Exception as e:
            print(f'Error: {e}.')
    



    def get_pod_runtime_detail(self, contents, *args, **kwargs):
        '''
        获取pod运行状态详情信息
        '''
        try:
            runtime_dict = {}

            pod_name = re.findall('\s*Name:\s*(.+)', contents)[0]
            namespace = re.findall('\s*Namespace:\s*(.+)', contents)[0]
            dist_node, node_ip = re.findall('\s*Node:\s*(.+)/(.+)', contents)[0]
            image_repo, image_version = re.findall('\s*Image:\s*(.+):(.+)', contents)[0]
            limit_cpu, limit_mem = re.findall('\s*Limits:\n\s*cpu:\s+(.+)\n\s*memory:\s+(.+)', contents)[0]
            request_cpu, request_mem = re.findall('\s*Requests:\n\s*cpu:\s+(.+)\n\s*memory:\s+(.+)', contents)[0]
            running_status = re.findall('\s*Status:\s*(.+)', contents)[0]
            ready_status = re.findall('\s*Ready:\s*(.+)', contents)[0]
            restart_time = re.findall('\s*Restart Count:\s*(.+)', contents)[0]
            pod_ip = re.findall('\s*IP:\s*(.+)', contents)[0]


            runtime_dict['name'] = pod_name
            runtime_dict['namespace'] = namespace
            runtime_dict['node'] = dist_node
            runtime_dict['node_ip'] = node_ip
            runtime_dict['pod_ip'] = pod_ip
            runtime_dict['image'] = image_repo
            runtime_dict['version'] = image_version
            runtime_dict['limits'] = limit_cpu + limit_mem
            runtime_dict['requests'] = request_cpu + request_mem
            runtime_dict['status'] = running_status
            runtime_dict['ready'] = ready_status
            runtime_dict['restart'] = restart_time

            return runtime_dict

        except Exception as e:
            print(f'Error: {e}.')




    def get_project_limit_spec(self, project_name, *args, **kwargs):
        '''
        根据 pod runtime 获取项目k8s资源模版
        '''
        try:
            pod_name       = self.get_project_pod_list(self.get_project_runtime(project_name))[0]
            runtime_detail = self.get_pod_runtime_detail(self.get_pod_detail_yaml(pod_name))
            
            return runtime_detail['limits']

        except Exception as e:
            print(f'Error: {e}.')



# if __name__ == '__main__':
  
#     host         = '192.168.3.33'
#     port         = 60022
#     username     = 'uniondrug'
#     pkey_path    = '/Users/shenlei/.ssh/id_rsa'