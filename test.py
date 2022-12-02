import logging

logger1 = logging.getLogger('myapp.area1')
logger2 = logging.getLogger('myapp.area2')
root = logging.getLogger()  # 不传参数或者参数为空字符串，返回root logger

# 新建一个handler，并添加到root logger中（也添加到其他的logge)
# 新建的handler将消息输出到myapp.log文件中
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='myapp.log',
                    filemode='w')

# 新建一个用于将消息输出到命令行的handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')  # name指的是logger名
console.setFormatter(formatter)

# root logger中添加console handler
root.addHandler(console)  # 如果这个改成使用logger1来添加的话，只会对logger1本身生效
 
# 使用root logger来打印消息
logging.info('Jackdaws love my big sphinx of quartz.')

# 使用自定义的logger来打印消息
logger1.debug('Quick zephyrs blow, vexing daft Jim.')
logger1.info('How quickly daft jumping zebras vex.')
logger2.warning('Jail zesty vixen who grabbed pay from quack.')
logger2.error('The five boxing wizards jump quickly.')

# 命令行输出
# root        : INFO     Jackdaws love my big sphinx of quartz.
# myapp.area1 : INFO     How quickly daft jumping zebras vex.
# myapp.area2 : WARNING  Jail zesty vixen who grabbed pay from quack.
# myapp.area2 : ERROR    The five boxing wizards jump quickly.

# myapp.log文件内容
# 12-01 20:31 root         INFO     Jackdaws love my big sphinx of quartz.
# 12-01 20:31 myapp.area1  DEBUG    Quick zephyrs blow, vexing daft Jim.
# 12-01 20:31 myapp.area1  INFO     How quickly daft jumping zebras vex.
# 12-01 20:31 myapp.area2  WARNING  Jail zesty vixen who grabbed pay from quack.
# 12-01 20:31 myapp.area2  ERROR    The five boxing wizards jump quickly.
