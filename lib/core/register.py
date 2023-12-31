#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

"""
用于注册互斥的参数并给出错误提示

Register()
 start         最少通过量
 stop          最大通过量
 mutex         互斥开关
 mutex_errmsg  错误提示

add()
 perform       目标函数
 trigger       触发条件
 args          参数传入
 kwargs        参数传入

Usage:
 r = Register()
 r.add(function1,1>1)
 r.add(function2,2>1)
 r.add(function3,3>1)
 r.run()

"""

# import types
import sys
from lib.core.data import logger
from lib.core.exception import RegisterDataException, RegisterMutexException, RegisterValueException

# 使用Register.add添加(target,trigger)，trigger的作用是控制是否执行target
# Register.run会运行满足条件的target
# Register还可以设置mutex=true，并且设置start和end的值，来实现可以执行target的个数
class Register:
    # mutex是互斥开关，如果mutex为true，那么可以执行的target的数量必须在[start，stop]范围内
    # mutex_errmsg是错误提示
    def __init__(self, start=1, stop=1, mutex_errmsg=None, mutex=True):
        self.targets = []
        self.mutex = mutex
        self.start = start
        self.stop = stop
        self.mutex_errmsg = mutex_errmsg
        self.verified = []

    def enable_mutex(self):
        self.mutex = True

    def set_mutex_errmsg(self, s):
        self.mutex_errmsg = str(s)

    # trigger为True或者非空表示执行perform，否则不执行perform
    # trigger字面意思为触发
    def add(self, perform, trigger, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        d = {'perform': perform, 'args': args, 'kwargs': kwargs, 'trigger': trigger}
        self.targets.append(d)
        self.__args = args
        self.__kwargs = kwargs

    # 执行perform(*args, **kwargs)
    def run(self):
        self.__pretreat()
        for target in self.verified:
            if not target.get('perform'):
                msg = 'Register has no verified target'
                raise RegisterDataException(msg)
            target.get('perform')(*target.get('args'), **target.get('kwargs'))

    # 将trigger为真/非空的target到verified中
    def __pretreat(self):
        # 检查target!=0、start<end
        self.__input_vector_check()
        
        for __target in self.targets:
            __trigger = __target.get('trigger')
            if type(__trigger) == bool or type(__trigger) == str:
                if __trigger:  # 如果trigger为真或非空
                    self.verified.append(__target)
            else:
                msg = '[Trigger Type Error] Expected:boolean,found:' + str(type(__trigger))
                raise RegisterValueException(msg)
        self.__mutex_check()

    # verified的范围必须在start和stop之间
    def __mutex_check(self):
        if self.mutex:
            if len(self.verified) < self.start or len(self.verified) > self.stop:
                if self.mutex_errmsg is None:
                    raise RegisterMutexException('mutex error,verified func count: ' + str(len(self.verified)))
                else:
                    sys.exit(logger.error(self.mutex_errmsg))

    # 检查target的数量、start和end的关系
    def __input_vector_check(self):
        if type(self.stop) == int and type(self.start) == int and type(
                self.mutex) == bool:
            pass
        else:
            raise RegisterValueException('Register init func type error')
        
        if len(self.targets) is 0:
            msg = 'no target'
            raise RegisterDataException(msg)
        
        if self.start > self.stop:
            msg = 'start > stop'
            raise RegisterDataException(msg)
