#!/usr/bin/env python3
# -*- coding:utf8 -*-

# 系统类
import os, sys, json, shutil
from collections import namedtuple

# 核心类
from ansible.parsing.dataloader import DataLoader       # 用于读取 yaml 和 json 格式文件
from ansible.vars.manager import VariableManager        # 用于管理各类变量信息（inventory、playbook等）
from ansible.inventory.manager import InventoryManager  # 用于导入 ansible 资产清单文件
from ansible.playbook.play import Play                  # 用于存储执行角色的信息
from ansible.executor.playbook_executor import PlaybookExecutor  # 用于执行 ansible playbook 模式
from ansible.executor.task_queue_manager import TaskQueueManager # 用于管理 ansible 底层调用的 task 队列
from ansible.plugins.callback import CallbackBase       # 状态回调基础类，用于显示各种成功失败状态信息
from ansible.errors import AnsibleParserError           # ansible 错误分析类，用于处理异常
import ansible.constants as C


class ResultCallback(CallbackBase):
    '''
    状态回调类: 成功失败状态二次处理
    '''
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(display=None)
        self.status_ok = json.dumps({})
        self.status_fail = json.dumps({})
        self.status_unreachable = json.dumps({})
        self.status_playbook = ''
        self.status_no_hosts = False
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}


    def v2_runner_on_ok(self, result, *args, **kwargs):
        # 运行成功
        host=result._host.get_name()
        self.runner_on_ok(host, result._result)
        # self.status_ok=json.dumps({host:result._result},indent=4)
        self.host_ok[host] = result


    def v2_runner_on_failed(self, result, ignore_errors=False, *args, **kwargs):
        # 运行正常
        host = result._host.get_name()
        self.runner_on_failed(host, result._result, ignore_errors)
        #self.status_fail=json.dumps({host:result._result},indent=4)
        self.host_failed[host] = result


    def v2_runner_on_unreachable(self, result, *args, **kwargs):
        # 主机不可达
        host = result._host.get_name()
        self.runner_on_unreachable(host, result._result)
        #self.status_unreachable=json.dumps({host:result._result},indent=4)
        self.host_unreachable[host] = result


    def v2_playbook_on_no_hosts_matched(self):
        # 不在playbook资产清单内
        self.playbook_on_no_hosts_matched()
        self.status_no_hosts=True
        

    def v2_playbook_on_play_start(self, play):
        # 开始运行
        self.playbook_on_play_start(play.name)
        self.playbook_path=play.name





class AnsibleAdHoc():
    '''
    ansible ad-hoc 运行类
    '''
    def __init__(self, extra_vars={},
                    host_list='/etc/ansible/hosts', 
                    connection='ssh', 
                    become=False,
                    become_method=None,
                    become_user=None,
                    module_path=None,
                    fork=100,
                    remote_user=None,
                    private_key_file_path=None,
                    ansible_cfg_path=None, 
                    password={},
                    *args, **kwargs):
        
        Options = namedtuple("Options", [
                "connection", "remote_user", "ask_sudo_pass", "verbosity", "ack_pass",
                "module_path", "forks", "become", "become_method", "become_user", "check",
                "listhosts", "listtasks", "listtags", "syntax", "sudo_user", "sudo", "diff"
            ])

        self.options = Options(connection=connection, 
                                remote_user=remote_user, 
                                ack_pass=None, sudo_user=None, sudo=None,
                                ask_sudo_pass=False, verbosity=5, forks=fork, 
                                module_path=module_path, become=become, 
                                become_method=become_method, become_user=become_user, 
                                check=False, diff=False,
                                listhosts=False, listtasks=False, 
                                listtags=False, syntax=False)
        
        self.loader    = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources='localhost, ')        
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.password = {}

        # if ansible_cfg != None:
            # os.environ["ANSIBLE_CONFIG"] = ansible_cfg_path


    def run(self, hosts, command, *args, **kwargs):
        
        tqm = None

        self.play_source = dict(
            name = "Ansible Play",
            hosts = hosts,
            gather_facts = 'no',
            tasks = [
                dict(action=dict(module='shell', args=command), register='shell_out'),
                dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
            ]
        )

        play_obj = Play().load(self.play_source, variable_manager=self.variable_manager, loader=self.loader)
        result_callback = ResultCallback()

        tqm_obj = TaskQueueManager(
            inventory = self.inventory,
            variable_manager = self.variable_manager,
            loader  = self.loader,
            options = self.options,
            passwords = self.password,
            stdout_callback = result_callback,
        )

        tqm_obj.run(play_obj)

        
        # result_raws = {
        #     "success": {},
        #     "failed": {},
        #     "unreachable": {}
        # }

        # for host, result in result_callback.host_ok.items():
        #     result_raws["success"][host] = result._result


        # for host, result in result_callback.host_failed.items():
        #     result_raws["failed"][host] = result_raws._result


        # for host, result in result_callback.host_unreachable.items():
        #     result_raws["unreachable"][host] =  result_raws._result

        # print(result_raws)



class AnsiblePalybook():
    '''
    ansible playbook 运行类
    '''
    def __init__(self, playbook_path, extra_vars={}, 
                    host_list='/etc/ansible/hosts', 
                    connection='ssh', 
                    become=False, 
                    become_method=None,
                    become_user=None,
                    module_path=None, 
                    fork=100,
                    remote_user=None,
                    private_key_file_path=None,
                    ansible_cfg_path=None, 
                    password={},
                    check=False,
                    *args, **kwargs):
        
        self.playbook_path = playbook_path
        self.password = password
        self.extra_vars = extra_vars
        Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
        self.options = Options(listtags=False, listtasks=False, 
                                listhosts=False, syntax=False, 
                                connection=connection, module_path=module_path, 
                                forks=fork, remote_user=remote_user, 
                                private_key_file=private_key_file_path, 
                                ssh_common_args=None, 
                                ssh_extra_args=None, 
                                sftp_extra_args=None, 
                                scp_extra_args=None, 
                                become=become, 
                                become_method=become_method, 
                                become_user=become_user, 
                                verbosity=None, check=check)
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources=['host'])        
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

        # if ansible_cfg != None:
            # os.environ["ANSIBLE_CONFIG"] = ansible_cfg_path


    def run(self):
        complex_msg = {}

        if not os.path.exists(self.playbook_path):
            code = 1000
            results={'playbook':self.playbook_path, 'msg':self.playbook_path + 'playbook is not exist', 'flag':False}


        playbook_exe = PlaybookExecutor(playbooks=[self.playbook_path],
                       inventory=self.inventory,
                       variable_manager=self.variable_manager,
                       loader=self.loader,
                       options=self.options,
                       passwords=self.password)

        self.results_callback = ResultCallback()




if __name__ == '__main__':

    hosts = '192.168.3.33'
    command = 'hostname'

    ADHoc   = AnsibleAdHoc()
    ADHoc.run(hosts, command)