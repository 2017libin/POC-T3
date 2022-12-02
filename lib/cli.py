#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

import os.path
import traceback
from lib.parse.cmdline import cmdLineParser
from lib.core.option import initOptions
from lib.controller.loader import loadModule, loadPayloads
from lib.core.common import setPaths, banner, systemQuit, openBrowser
from lib.core.data import paths, conf, logger, cmdLineOptions  # 这四个变量是类型为dict的实例
from lib.core.enums import EXIT_STATUS
from lib.core.settings import IS_WIN
from lib.core.exception import ToolkitUserQuitException
from lib.core.exception import ToolkitMissingPrivileges
from lib.core.exception import ToolkitSystemException
from lib.controller.engine import run
from thirdparty.colorama.initialise import init as winowsColorInit


def main():
    """
    Main function of POC-T when running from command line.
    """
    try:
        # 添加属性ROOT_PATH
        paths.ROOT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        try:
            os.path.isdir(paths.ROOT_PATH)
        except UnicodeEncodeError:
            errMsg = "your system does not properly handle non-ASCII paths. "
            errMsg += "Please move the project root directory to another location"
            logger.error(errMsg)
            raise SystemExit
        
        # 将data、script、ooutput等绝对路径添加到paths中
        setPaths()

        # 将命令选项进行解析，并将结果添加到cmdLineOptions中
        cmdLineOptions.update(cmdLineParser().__dict__)
        
        # 根据命令行参数来设置conf
        initOptions(cmdLineOptions)
        
        # 如果是WIN平台
        if IS_WIN:
            winowsColorInit()
            
        # 打印banner信息
        banner()

        # 设置th.module_obj
        loadModule()
        
        # 设置th.queue，存入target
        loadPayloads()

        # 
        run()

        if conf.OPEN_BROWSER:
            openBrowser()

        systemQuit(EXIT_STATUS.SYSETM_EXIT)

    except ToolkitMissingPrivileges, e:
        logger.error(e)
        systemQuit(EXIT_STATUS.ERROR_EXIT)
    
    except ToolkitSystemException, e:
        logger.error(e)
        systemQuit(EXIT_STATUS.ERROR_EXIT)

    except ToolkitUserQuitException:
        systemQuit(EXIT_STATUS.USER_QUIT)
    except KeyboardInterrupt:
        systemQuit(EXIT_STATUS.USER_QUIT)

    except Exception:
        print traceback.format_exc()
        logger.warning('It seems like you reached a unhandled exception, please report it to author\'s mail:<i@cdxy.me> or raise a issue via:<https://github.com/Xyntax/POC-T/issues/new>.')

if __name__ == "__main__":
    main()
