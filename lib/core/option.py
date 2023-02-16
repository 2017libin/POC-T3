#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

import os
import glob
import time
import sys
from lib.core.data import conf, paths, th, logger
from lib.core.enums import TARGET_MODE_STATUS, ENGINE_MODE_STATUS
from lib.utils.update import update
from lib.core.enums import API_MODE_NAME
from lib.core.register import Register

# 为conf添加不同的属性
def initOptions(args):
    # 检查是否需要更新版本
    checkUpdate(args)
    
    # 检查是否需要输出脚本信息
    # 如果需要输出，输出结束后结束程序
    checkShow(args)
    
    # Register就是根据命令行参数，来为conf添加属性
    # 设置使用的多线程
    EngineRegister(args)  # 设置属性 ENGINE 和 THREADS_NUM
    
    # 设置脚本
    ScriptRegister(args)  # 设置属性 
    
    # 扫描目标
    TargetRegister(args)
    
    # 生成扫描目标的搜索引擎
    ApiRegister(args)

    # 输出方式
    Output(args)
    
    # 其他设置
    Misc(args)


def checkUpdate(args):
    if args.sys_update:
        update()

def checkShow(args):
    show_scripts = args.show_scripts
    if show_scripts:
        # 获取所有paths.SCRIPT_PATH目录下以.py结尾的文件的绝对路径
        module_name_list = glob.glob(os.path.join(paths.SCRIPT_PATH, '*.py'))
        msg = 'Script Name (total:%s)\n' % str(len(module_name_list) - 1)
        for each in module_name_list:
            # 分隔路径和带后缀的文件名
            filename_ext = os.path.split(each)[1]
            # 分隔文件名和后缀
            filename = os.path.splitext(filename_ext)[0]
            if filename != '__init__':
                msg += '  %s\n' % filename
        sys.exit(logger.info(msg))  # 输出msg并且结束程序

# 设置 conf.ENGINE：ENGINE_MODE_STATUS.THREAD 或者 ENGINE_MODE_STATUS.GEVENT
# 设置 conf.THREADS_NUM：0 < thread_num < 101
# 设置 th.THREADS_NUM：0 < thread_num < 101
def EngineRegister(args):
    # 设置使用的多线程方式以及线程数
    thread_status = args.engine_thread
    gevent_status = args.engine_gevent
    thread_num = args.thread_num

    def __thread():
        conf.ENGINE = ENGINE_MODE_STATUS.THREAD

    def __gevent():
        conf.ENGINE = ENGINE_MODE_STATUS.GEVENT

    # 默认使用thread
    conf.ENGINE = ENGINE_MODE_STATUS.THREAD  # default choice

    msg = 'Use [-eT] to set Multi-Threaded mode or [-eG] to set Coroutine mode.'
    # 两个都为false或者选择了其中一个ENGINE
    r = Register(mutex=True, start=0, stop=1, mutex_errmsg=msg)
    r.add(__thread, thread_status)
    r.add(__gevent, gevent_status)
    r.run()
    # 检查线程数
    if 0 < thread_num < 101:
        # th和conf新增属性THREADS_NUM
        th.THREADS_NUM = conf.THREADS_NUM = thread_num
    else:
        msg = 'Invalid input in [-t], range: 1 to 100'
        sys.exit(logger.error(msg))

# 设置conf.MODULE_NAME：模块名，例如 tets.py
# 设置conf.MODULE_FILE_PATH：模块的绝对路径，例如/home/chase511/code/py-code/POC-T/script/test.py
def ScriptRegister(args):
    

    # handle input: nothing
    if not args.script_name and not args.scripts_file:
        msg = 'Use -s or -sF to load script. Example: [-s spider] or [-sF ./scripts.txt]'
        sys.exit(logger.error(msg))
    
    conf.MODULE_NAME = set()
    # 从文件中导入多个脚本
    if args.scripts_file:
        with open(args.scripts_file, "r") as f:
            for script_name in f.readlines():
                script_name = script_name.strip()
                logger.info(f"finding {script_name}...")
                if not script_name.endswith('.py'):
                    script_name += '.py'
                _path = os.path.abspath(os.path.join(paths.SCRIPT_PATH, script_name))
                if os.path.isfile(_path):
                    conf.MODULE_NAME.add(script_name)
                    # conf.MODULE_NAME = script_name
                    # conf.MODULE_FILE_PATH = os.path.abspath(_path)
                else:
                    msg = 'Script [%s] not exist. Use [--show] to view all available script in ./script/' % input_path
                    sys.exit(logger.error(msg))

    # 导入单个脚本
    if args.script_name:
        input_path = args.script_name
        # handle input: "-s ./script/spider.py" 
        if os.path.split(input_path)[0]:  # 如果输入为 spider.py  split的结果为('', 'spider.py')
            if os.path.exists(input_path):
                if os.path.isfile(input_path):
                    if input_path.endswith('.py'):
                        conf.MODULE_NAME.add(os.path.split(input_path)[-1])
                        # conf.MODULE_NAME = os.path.split(input_path)[-1]
                        # conf.MODULE_FILE_PATH = os.path.abspath(input_path)
                    else:
                        msg = '[%s] not a Python file. Example: [-s spider] or [-s ./script/spider.py]' % input_path
                        sys.exit(logger.error(msg))
                else:
                    msg = '[%s] not a file. Example: [-s spider] or [-s ./script/spider.py]' % input_path
                    sys.exit(logger.error(msg))
            else:
                msg = '[%s] not found. Example: [-s spider] or [-s ./script/spider.py]' % input_path
                sys.exit(logger.error(msg))

        # handle input: "-s spider"  "-s spider.py"
        else:
            if not input_path.endswith('.py'):
                input_path += '.py'
            _path = os.path.abspath(os.path.join(paths.SCRIPT_PATH, input_path))
            if os.path.isfile(_path):
                conf.MODULE_NAME.add(input_path)
                # conf.MODULE_NAME = input_path
                # conf.MODULE_FILE_PATH = os.path.abspath(_path)
            else:
                msg = 'Script [%s] not exist. Use [--show] to view all available script in ./script/' % input_path
                sys.exit(logger.error(msg))

# 根据不同的target类型来设置conf

# 类型1：随机生成或者从命令行/文件读取target（目标）
    # target_file：从文件读取目标
    # target_single：单一扫描目标
    # target_network：生成指定网络的IP
    # target_array：生成指定范围的整型数组
    # target_subdomains：从文件中的域名列表生成子域名

# 类型2：通过API（搜索引擎）生成target
    # api_zoomeye
    # api_shodan
    # api_google
    # api_fofa
def TargetRegister(args):
    input_file = args.target_file
    domain_file = args.domain_file
    input_single = args.target_single
    input_network = args.target_network
    input_array = args.target_array
    api_zoomeye = args.zoomeye_dork
    api_shodan = args.shodan_dork
    api_google = args.google_dork
    api_fofa = args.fofa_dork

    def __file():
        if not os.path.isfile(input_file):
            msg = 'TargetFile not found: %s' % input_file
            sys.exit(logger.error(msg))
        conf.TARGET_MODE = TARGET_MODE_STATUS.FILE
        conf.INPUT_FILE_PATH = input_file

    def __subdomain():
        if not os.path.isfile(domain_file):
            msg = 'DomainsFile not found: %s' % domain_file
            sys.exit(logger.error(msg))
        conf.TARGET_MODE = TARGET_MODE_STATUS.SUBDOMAIN
        conf.INPUT_DOMAIN_FILE_PATH = domain_file
    
    def __array():
        help_str = "Invalid input in [-iA], Example: -iA 1-100"
        try:
            _int = input_array.strip().split('-')
            if int(_int[0]) < int(_int[1]):
                if int(_int[1]) - int(_int[0]) > 1000000:
                    warnMsg = "Loading %d targets, Maybe it's too much, continue? [y/N]" % (
                        int(_int[1]) - int(_int[0]))
                    logger.warning(warnMsg)
                    a = input()
                    if a in ('Y', 'y', 'yes'):
                        pass
                    else:
                        msg = 'User quit!'
                        sys.exit(logger.error(msg))
            else:
                sys.exit(logger.error(help_str))
        except Exception:
            sys.exit(logger.error(help_str))
        conf.TARGET_MODE = TARGET_MODE_STATUS.RANGE
        conf.I_NUM2 = input_array
        conf.INPUT_FILE_PATH = None

    def __network():
        conf.TARGET_MODE = TARGET_MODE_STATUS.IPMASK
        conf.NETWORK_STR = input_network
        conf.INPUT_FILE_PATH = None

    def __single():
        conf.TARGET_MODE = TARGET_MODE_STATUS.SINGLE
        conf.SINGLE_TARGET_STR = input_single
        th.THREADS_NUM = conf.THREADS_NUM = 1
        conf.INPUT_FILE_PATH = None

    def __zoomeye():
        conf.TARGET_MODE = TARGET_MODE_STATUS.API
        conf.API_MODE = API_MODE_NAME.ZOOMEYE
        conf.API_DORK = api_zoomeye

    def __shodan():
        conf.TARGET_MODE = TARGET_MODE_STATUS.API
        conf.API_MODE = API_MODE_NAME.SHODAN
        conf.API_DORK = api_shodan

    def __google():
        conf.TARGET_MODE = TARGET_MODE_STATUS.API
        conf.API_MODE = API_MODE_NAME.GOOGLE
        conf.API_DORK = api_google

    def __fofa():
        conf.TARGET_MODE = TARGET_MODE_STATUS.API
        conf.API_MODE = API_MODE_NAME.FOFA
        conf.API_DORK = api_fofa

    msg = 'Please load targets with [-iS|-iA|-iF|-iN] or use API with [-aZ|-aS|-aG|-aF]'
    # 只能一个生效，最终只能运行其中一个函数
    # mutex为True表示互斥，也就是添加的函数只能运行其中一个
    r = Register(mutex=True, mutex_errmsg=msg)  # 默认start=end=1
    r.add(__file, input_file)
    r.add(__subdomain, domain_file)
    r.add(__network, input_network)
    r.add(__array, input_array)
    r.add(__single, input_single)
    r.add(__zoomeye, api_zoomeye)
    r.add(__shodan, api_shodan)
    r.add(__google, api_google)
    r.add(__fofa, api_fofa)
    r.run()

# 设置conf.offset：
# 设置conf.limit
# 如果API类型为ZOOMEYE，设置conf.ZOOMEYE_SEARCH_TYPE
# 如果API类型为GOOGLE，设置conf.GOOGLE_PROXY
def ApiRegister(args):
    search_type = args.search_type
    offset = args.api_offset
    google_proxy = args.google_proxy
    api_limit = args.api_limit

    # 如果conf不具有API_MODE属性，即不是通过API生成target
    if not 'API_MODE' in conf:
        return

    if not conf.API_DORK:
        msg = 'Empty API dork, show usage with [-h]'
        sys.exit(logger.error(msg))

    if offset < 0:
        msg = 'Invalid value in [--offset], show usage with [-h]'
        sys.exit(logger.error(msg))
    else:
        conf.API_OFFSET = offset

    # handle typeError in cmdline.py
    if api_limit <= 0:
        msg = 'Invalid value in [--limit], show usage with [-h]'
        sys.exit(logger.error(msg))
    else:
        conf.API_LIMIT = api_limit

    if conf.API_MODE is API_MODE_NAME.ZOOMEYE:
        if search_type not in ['web', 'host']:
            msg = 'Invalid value in [--search-type], show usage with [-h]'
            sys.exit(logger.error(msg))
        else:
            conf.ZOOMEYE_SEARCH_TYPE = search_type

    elif conf.API_MODE is API_MODE_NAME.GOOGLE:
        conf.GOOGLE_PROXY = google_proxy

# 设置conf.SCREEN_OUTPUT
# 设置conf.FILE_OUTPUT
# 设置conf.OUTPUT_FILE_PATH
def Output(args):
    output_file = args.output_path
    file_status = args.output_file_status
    screen_status = args.output_screen_status
    browser = args.open_browser

    # not file_status为真：表示不输出到文件
    # output_file非空：表示设置了输出文件名
    if not file_status and output_file:
        msg = 'Cannot use [-oF] and [-o] together, please read the usage with [-h].'
        sys.exit(logger.error(msg))

    # not file_status为真：表示不输出到文件
    # browser为真：表示打开浏览器
    if not file_status and browser:
        msg = '[--browser] is based on file output, please remove [-oF] in your command and try again.'
        sys.exit(logger.error(msg))

    conf.SCREEN_OUTPUT = screen_status
    conf.FILE_OUTPUT = file_status
    # 如果指定文件名，则根据文件名生成绝对路径
    # 如果不指定文件名，则随机生成文件名并扩充为绝对路径
    conf.OUTPUT_FILE_PATH = os.path.abspath(output_file) if output_file else \
        os.path.abspath(
            os.path.join(
                paths.OUTPUT_PATH, time.strftime(
                    '[%Y%m%d-%H%M%S]', time.localtime(
                        time.time())) + '-'.join(conf.MODULE_NAME) + '.txt'))

# 设置conf.SINGLE_MODE
# 设置conf.OPEN_BROWSER
def Misc(args):
    conf.SINGLE_MODE = args.single_mode
    conf.OPEN_BROWSER = args.open_browser
