#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

import threading
import time
import traceback
from lib.core.data import th, conf, logger
from lib.core.common import dataToStdout
from lib.utils.console import getTerminalSize
from lib.utils.versioncheck import PYVERSION
from lib.core.enums import POC_RESULT_STATUS, ENGINE_MODE_STATUS

# 设置th中的相关信息
def initEngine():
    th.thread_mode = True if conf.ENGINE is ENGINE_MODE_STATUS.THREAD else False  # 如果是Thread为True，是gevent则为False
    th.poc_name = conf.POC_NAME
    th.f_flag = conf.FILE_OUTPUT  # 标记是否输出文件
    th.s_flag = conf.SCREEN_OUTPUT  # 标记是否输出到屏幕
    th.output = conf.OUTPUT_FILE_PATH  # 输出的文件路径
    th.thread_count = th.threads_num = th.THREADS_NUM  # 输出的线程数
    th.single_mode = conf.SINGLE_MODE  # 单例模式
    th.scan_count = th.found_count = 0  # 已经扫描以及满足条件的target个数
    th.console_width = getTerminalSize()[0] - 2  # 控制台宽度
    th.is_continue = True  # 是否继续
    th.found_single = False  # 是否发现一个
    th.start_time = time.time()  # 开始时间
    # 线程锁是不是只有多线程才需要设置？应该加一个条件判断？
    setThreadLock()  # 设置线程锁
    msg = 'Set the number of concurrent: %d' % th.threads_num
    logger.success(msg)

# 设置th，停止扫描
def singleMode():
    th.is_continue = False
    th.found_single = True

# target 指的是测试目标
# module_obj 指的是使用的测试脚本
def scan():
    while 1:
        # 如果是多线程，那么上锁
        # 这里的上锁操作不能放到if语句判断之后！！考虑一下临界值大小为1的情况
        if th.thread_mode:
            th.load_lock.acquire()
        
        # 如果剩余的目标大于0并且需要继续扫描
        if th.queue.qsize() > 0 and th.is_continue:
            # 这里的job就是包含target、poc_name和poc_obj的字典
            job = th.queue.get(timeout=1.0)
            if th.thread_mode:
                th.load_lock.release()
        else:
            if th.thread_mode:
                th.load_lock.release()
            break
        try:
            # POC在执行时报错如果不被处理，线程框架会停止并退出
            # 执行poc模块中的poc函数，返回的status有三种可能
            status = job["poc_module"].poc(job["target"])
            resultHandler(status, job)  # 处理结果
        except Exception:
            th.errmsg = traceback.format_exc()
            th.is_continue = False
        # 已扫描的目标个数加1
        changeScanCount(1)
        # 判断是否需要将扫描时的信息进行输出
        if th.s_flag:
            printProgress()
    if th.s_flag:
        printProgress()
    
    # Thread_count应该表示的是还在执行的子线程
    changeThreadCount(-1)

def run():
    # 初始化Engine
    initEngine()
    if conf.ENGINE is ENGINE_MODE_STATUS.THREAD:  # 如果engine使用thread
        # >>> 原来的写法
        # for i in range(th.threads_num):
        #     t = threading.Thread(target=scan, name=str(i))
        #     setThreadDaemon(t)
        #     t.start()
        # # It can quit with Ctrl-C
        # # 相当于做了join操作？
        # while 1:
        #     if th. > 0 and th.is_continue:
        #         time.sleep(0.01)
        #     else:
        #         break
        
        # >>> 改动的写法
        thread_list = []
        # 新建子线程
        for i in range(th.threads_num):
            t = threading.Thread(target=scan)
            # 这里应该可以省略
            # setThreadDaemon(t)
            t.start()
            thread_list.append(t)
        
        # 等待子线程结束
        for t in thread_list:
            t.join()
        
    # 如果engine使用gevent（协程，单线程异步）
    elif conf.ENGINE is ENGINE_MODE_STATUS.GEVENT:
        from gevent import monkey
        monkey.patch_all()  # 将所有耗时的操作转换为gevent实现，来实现自动切换
        import gevent
        while th.queue.qsize() > 0 and th.is_continue:
            gevent.joinall([gevent.spawn(scan) for i in xrange(0, th.threads_num) if
                            th.queue.qsize() > 0])
    dataToStdout('\n')

    if 'errmsg' in th:
        logger.error(th.errmsg)
    
    if th.found_single:
        msg = "[single-mode] found!"
        logger.info(msg)
    

def resultHandler(status, payload):
    # poc函数返回值是：不通过
    if not status or status is POC_RESULT_STATUS.FAIL:  
        return
    
    # poc函数返回值是：重试
    if status is POC_RESULT_STATUS.RETRAY:
        # 刚刚的扫描不算数，重新将payload放回到队列中（payload就是target）
        changeScanCount(-1)
        # 这里需要上锁？
        th.queue.put(payload)
        return

    # poc函数返回值是：通过
    if status is True or status is POC_RESULT_STATUS.SUCCESS:
        msg = f'{payload["poc_name"]}: {payload["target"]}'
    else:
        msg = f'{payload["poc_name"]}: {str(status)}'
    
    # 找到满足条件的目标数量foundcount加1
    changeFoundCount(1)
    
    # 输出到命令行
    if th.s_flag:
        printMessage(msg)
        
    # 输出到文件
    if th.f_flag:
        output2file(msg)
    
    # 如果是单例模式
    if th.single_mode:
        singleMode()

# 设置线程锁
def setThreadLock():
    if th.thread_mode:
        th.found_count_lock = threading.Lock()
        th.scan_count_lock = threading.Lock()
        th.thread_count_lock = threading.Lock()
        th.file_lock = threading.Lock()  
        th.load_lock = threading.Lock()

def setThreadDaemon(thread):
    # Reference: http://stackoverflow.com/questions/190010/daemon-threads-explanation
    if PYVERSION >= "2.6":
        thread.daemon = True
    else:
        thread.setDaemon(True)


def changeFoundCount(num):
    if th.thread_mode: th.found_count_lock.acquire()
    th.found_count += num
    if th.thread_mode: th.found_count_lock.release()

# 改变已经扫描的目标的计数
def changeScanCount(num):
    if th.thread_mode: th.scan_count_lock.acquire()
    th.scan_count += num
    if th.thread_mode: th.scan_count_lock.release()

# 修改线程数
def changeThreadCount(num):
    if th.thread_mode: th.thread_count_lock.acquire()
    th.thread_count += num
    if th.thread_mode: th.thread_count_lock.release()

# 
def printMessage(msg):
    dataToStdout('\r' + msg + ' ' * (th.console_width - len(msg)) + '\n\r')

# 打印当前扫描的状态
def printProgress():
    msg = '%s found | %s remaining | %s scanned in %.2f seconds' % (
        th.found_count, th.queue.qsize(), th.scan_count, time.time() - th.start_time)
    out = '\r' + ' ' * (th.console_width - len(msg)) + msg
    dataToStdout(out)


def output2file(msg):
    if th.thread_mode: th.file_lock.acquire()
    f = open(th.output, 'a')
    f.write(msg + '\n')
    f.close()
    if th.thread_mode: th.file_lock.release()
