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
    th.module_name = conf.MODULE_NAME
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
    setThreadLock()  # 设置线程锁
    msg = 'Set the number of concurrent: %d' % th.threads_num
    logger.success(msg)

# 设置th，停止扫描
def singleMode():
    th.is_continue = False
    th.found_single = True

# 
def scan():
    while 1:
        if th.thread_mode: th.load_lock.acquire()
        if th.queue.qsize() > 0 and th.is_continue:
            payload = str(th.queue.get(timeout=1.0))
            if th.thread_mode: th.load_lock.release()
        else:
            if th.thread_mode: th.load_lock.release()
            break
        try:
            # POC在执行时报错如果不被处理，线程框架会停止并退出
            status = th.module_obj.poc(payload)  # 执行模块中的poc函数，返回一个bool值表示验证是否通过
            resultHandler(status, payload)  # 处理结果
        except Exception:
            th.errmsg = traceback.format_exc()
            th.is_continue = False
        # 扫描的target个数加1
        changeScanCount(1)
        
        if th.s_flag:
            printProgress()
    if th.s_flag:
        printProgress()
    
    # Thread_count应该表示的是正在执行
    changeThreadCount(-1)

def run():
    # 初始化Engine
    initEngine()
    if conf.ENGINE is ENGINE_MODE_STATUS.THREAD:  # 如果engine使用thread
        for i in range(th.threads_num):
            t = threading.Thread(target=scan, name=str(i))
            setThreadDaemon(t)
            t.start()
        # It can quit with Ctrl-C
        # 相当于做了join操作？
        while 1:
            if th.thread_count > 0 and th.is_continue:
                time.sleep(0.01)
            else:
                break
    
    elif conf.ENGINE is ENGINE_MODE_STATUS.GEVENT:  # 如果engine使用gevent
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
    # poc返回值是：不通过
    if not status or status is POC_RESULT_STATUS.FAIL:  
        return
    # poc返回值是：重试
    elif status is POC_RESULT_STATUS.RETRAY:
        # 刚刚的扫描不算数，重新将payload放回到队列中（payload就是target）
        changeScanCount(-1)
        th.queue.put(payload)
        return
    # poc返回值是：通过
    elif status is True or status is POC_RESULT_STATUS.SUCCESS:
        msg = payload
    else:
        msg = str(status)
    
    # 标记找到一个target通过poc
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
