#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

import os
import subprocess

VERSION = '1.0.0'
PROJECT = "babySRC"
AUTHOR = 'aoaoao'
MAIL = 'xxx@qq.com'
PLATFORM = os.name
LICENSE = 'GPLv2'
IS_WIN = subprocess._mswindows

# essential methods/functions in custom scripts/PoC (such as function poc())
ESSENTIAL_POC_MODULE_METHODS = ['poc']

ESSENTIAL_TARGET_MODULE_METHODS = ['get_targets']


# Encoding used for Unicode data
UNICODE_ENCODING = "utf-8"

# String representation for NULL value
NULL = "NULL"

# Format used for representing invalid unicode characters
INVALID_UNICODE_CHAR_FORMAT = r"\x%02x"

ISSUES_PAGE = "https://github.com/Xyntax/POC-T/issues"

GIT_REPOSITORY = "git://github.com/Xyntax/POC-T.git"

GIT_PAGE = "https://github.com/Xyntax/POC-T"

# BANNER = """\033[01;34m
#                                              \033[01;31m__/\033[01;34m
#     ____     ____     _____           ______\033[01;33m/ \033[01;31m__/\033[01;34m
#    / __ \   / __ \   / ___/   ____   /__  __/\033[01;33m_/\033[01;34m
#   / /_/ /  / /_/ /  / /___   /___/     / /
#  / /___/   \____/   \____/            / /
# /_/                                  /_/
#     \033[01;37m{\033[01;m Version %s by %s mail:%s \033[01;37m}\033[0m
# \n""" % (VERSION, AUTHOR, MAIL)

BANNER = """
\033[01;34m
 /$$                 /$$                  /$$$$$$  /$$$$$$$   /$$$$$$
| $$                | $$                 /$$__  $$| $$__  $$ /$$__  $$
| $$$$$$$   /$$$$$$ | $$$$$$$  /$$   /$$| $$  \__/| $$  \ $$| $$  \__/
| $$__  $$ |____  $$| $$__  $$| $$  | $$|  $$$$$$ | $$$$$$$/| $$      
| $$  \ $$  /$$$$$$$| $$  \ $$| $$  | $$ \____  $$| $$__  $$| $$      
| $$  | $$ /$$__  $$| $$  | $$| $$  | $$ /$$  \ $$| $$  \ $$| $$    $$
| $$$$$$$/|  $$$$$$$| $$$$$$$/|  $$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$/
|_______/  \_______/|_______/  \____  $$ \______/ |__/  |__/ \______/ 
                               /$$  | $$                              
                              |  $$$$$$/                              
                               \______/           
\033[01;37m 
              {\033[01;mVersion %s by %s mail:%s}\033[0m
\033[01;37m
""" % (VERSION, AUTHOR, MAIL)                    

