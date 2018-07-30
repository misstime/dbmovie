# -*- coding: utf-8 -*-
"""
入口脚本
========
    命令行格式如：
        python cmd.py
            先抓列表页，再抓详情页；保存页面到硬盘；
            正常情况下：执行此命令进行抓取、更新。
        python cmd.py --type=info --saveHtml=0
            只抓详情页；不保存页面到硬盘；
        python cmd.py --type=info --miss=10987689-09876789-8909987
            只抓详情页；不保存页面到硬盘；

    命令行参数如下：
        type -- 页面类型（默认：'all'）
            'list'  ： 列表页
            'info'  ： 详情页
            'all'   ： 先抓列表页，再抓详情页
        saveHtml -- 是否保存抓取到的页面到硬盘（默认：'yes'）
            'yes'   ： 保存
            'no'    ： 不保存
        miss -- 抓取失败的页面，重新抓取
                因为网络等原因，部分页面可能会抓取失败
                miss参数格式：xxx-xxx
"""
__author__ = 'stephen'

import sys
import time
import getopt
import logging

from config import log_cfg

class Cmd(object):
    '''命令解析类'''

    def _get_opts(self):
        '''获取命令行参数'''
        try:
            opts, args = getopt.getopt(sys.argv[1:], '', ['type=', 'saveHtml=', 'miss='])
            return (opts, args)
        except getopt.GetoptError as e:
            exit(f'getopt.GetoptError: {e}')

    def _init_cmd_cfg(self, opts, args):
        '''根据命令行参数，初始化程序运行参数'''
        cmd_cfg = {
            'type': 'all',
            'saveHtml': 'yes',
            'miss': ''
        }
        for opt_name, opt_value in opts:
            if opt_name == '--type':
                if opt_value == 'list':
                    cmd_cfg['type'] = 'list'
                elif opt_value == 'info':
                    cmd_cfg['type'] = 'info'
            if opt_name == '--saveHtml':
                if opt_value == 'no':
                    cmd_cfg['saveHtml'] = False
            if opt_name == '--miss':
                cmd_cfg['miss'] = opt_value
        return cmd_cfg

    def _route(self, cmd_cfg):
        '''路由'''
        if cmd_cfg['type'] == 'list':
            from spider.list import List
            list = List(cmd_cfg)
            if cmd_cfg['miss']:
                list.miss()
            else:
                list.run()
        elif cmd_cfg['type'] == 'info':
            from spider.info import Info
            info = Info(cmd_cfg)
            if cmd_cfg['miss']:
                info.miss()
            else:
                info.run()
        elif cmd_cfg['type'] == 'all':
            from spider.list import List
            from spider.info import Info
            list = List(cmd_cfg)
            list.run()
            info = Info(cmd_cfg)
            info.run()
        else:
            exit(f"cmd type 未定义：{cmd_cfg['type']}")

    def _execute(self):
        '''执行'''
        opts, args = self._get_opts()                # 获取命令行参数
        cmd_cfg = self._init_cmd_cfg(opts, args)     # 根据命令行参数，初始化程序运行参数
        self._route(cmd_cfg)                         # 路由

if __name__ == '__main__':
    cmd = Cmd()
    cmd._execute()
















