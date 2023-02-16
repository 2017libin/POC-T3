#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

import queue as Queue
import sys
import imp
import os
from lib.core.data import th, conf, logger, paths
from lib.core.enums import API_MODE_NAME, TARGET_MODE_STATUS
from lib.core.settings import ESSENTIAL_MODULE_METHODS
from lib.core.exception import ToolkitValueException
from lib.controller.api import runApi
from thirdparty.IPy import IPy

# 设置 th.module_obj,th.module_obj指向需要执行的script文件，即poc文件
def loadModule():
    _name = conf.MODULE_NAME
    msg = 'Load custom script: %s' % _name
    logger.success(msg)

    # imp提供了实现import语句的功能
    fp, pathname, description = imp.find_module(os.path.splitext(_name)[0], [paths.SCRIPT_PATH])
    try:
        # 用来加载find_module找到的模块，第一个参数可以乱填？
        th.module_obj = imp.load_module("_", fp, pathname, description)  # imp.load_module(name, file, pathname, description)
        # 检查脚本文件中是否包含有必要的函数，即poc函数
        for each in ESSENTIAL_MODULE_METHODS:
            if not hasattr(th.module_obj, each):  
                errorMsg = "Can't find essential method:'%s()' in current script，Please modify your script/PoC."
                sys.exit(logger.error(errorMsg))
    except ImportError as e:
        errorMsg = "Your current scipt [%s.py] caused this exception\n%s\n%s" \
                   % (_name, '[Error Msg]: ' + str(e), 'Maybe you can download this module from pip or easy_install')
        sys.exit(logger.error(errorMsg))

# 根据target的模式，从不同的方式导入target到th.queue中
def loadPayloads():
    infoMsg = 'Initialize targets...'
    logger.success(infoMsg)
    th.queue = Queue.Queue()
    
    # 获取目标
    if conf.TARGET_MODE is TARGET_MODE_STATUS.RANGE:
        int_mode()
    elif conf.TARGET_MODE is TARGET_MODE_STATUS.FILE:
        file_mode()
    elif conf.TARGET_MODE is TARGET_MODE_STATUS.IPMASK:
        net_mode()
    elif conf.TARGET_MODE is TARGET_MODE_STATUS.SINGLE:
        single_target_mode()
    elif conf.TARGET_MODE is TARGET_MODE_STATUS.API:
        api_mode()
    elif conf.TARGET_MODE is TARGET_MODE_STATUS.SUBDOMAIN:
        subdomain_mode()
    else:
        raise ToolkitValueException('conf.TARGET_MODE value ERROR.')
    
    # 将目标和模块绑定
    
    logger.success('Total: %s' % str(th.queue.qsize()))


def file_mode():
    for line in open(conf.INPUT_FILE_PATH):
        sub = line.strip()
        if sub:
            th.queue.put(sub)

def int_mode():
    _int = conf.I_NUM2.strip().split('-')
    for each in range(int(_int[0].strip()), int(_int[1].strip())):
        th.queue.put(str(each))

def net_mode():
    ori_str = conf.NETWORK_STR
    try:
        _list = IPy.IP(ori_str)
    except Exception as e:
        sys.exit(logger.error('Invalid IP/MASK,%s' % e))
    for each in _list:
        th.queue.put(str(each))

def single_target_mode():
    th.queue.put(str(conf.SINGLE_TARGET_STR))

def api_mode():
    # api搜索结果的保存路径，路径不存在则新建
    conf.API_OUTPUT = os.path.join(paths.DATA_PATH, conf.API_MODE)
    if not os.path.exists(conf.API_OUTPUT):
        os.mkdir(conf.API_OUTPUT)
    
    file = runApi()
    for line in open(file):
        sub = line.strip()
        if sub:
            th.queue.put(sub)

def subdomain_mode():
    import thirdparty.subDomainsBrute.subDomainsBrute as subDomainsBrute
    import plugin.nowaf as nowaf
    # import glob
    
    output_file_list = []
    # 读取 domain_file 中的每一个域名来求出子域名
    for line in open(conf.INPUT_DOMAIN_FILE_PATH):
        sub = line.strip()
        if sub:
            # 创建临时文件存放结果
            root_path = os.path.dirname(os.path.abspath(__file__))
            tmp_dir = os.path.join(root_path, 'tmp')
            output_file = os.path.join(tmp_dir, f'{sub}_subdomains.txt')
            output_file_list.append(output_file)
            
            # 如果不存在文件夹则新建
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            
            # 如果已存在文件则删除（bushi）
            # 直接使用历史的查询结果
            if os.path.exists(output_file):
                continue
                # os.remove(tmp_file)
            
            # 设置枚举子域名的相关选项
            options = subDomainsBrute.Optios()
            options.no_cert_check = True
            options.output = output_file
            
            subDomainsBrute.subDomainsBrute(sub, options=options)
            # sys.exit(logger.info("exited by aoaoao"))
    
    # 将所有的扫描结果放入集合进行去重
    all_subdomains = set()
    for _file in output_file_list:
        with open(_file, 'r') as tmp_f:
            for domain in tmp_f:
                domain = domain.split()[0]
                if domain not in all_subdomains:
                    all_subdomains.add(domain)       # cname query can result in duplicated domains
    
    
    
    # 将过滤后的子域名加入队列作为测试目标
    for subdomains in all_subdomains:   
        th.queue.put(str(subdomains))
    
    # 过滤出没有waf的子域名？可访问的域名？
    th.queue = nowaf.nowaf_multithread(th.queue)
    
    # print(f"size of th.queue is {th.queue.qsize()}")
    # while not th.queue.empty():
    #     print(th.queue.get())
    
    # 调试信息
    # print(all_subdomains)
    # sys.exit(logger.info("exited by aoaoao"))