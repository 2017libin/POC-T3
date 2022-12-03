import configparser 

# 新建一个configparse对象
cf = configparser.ConfigParser() 

# 将配置文件内容读到对象中
cf.read("./data/test.conf") 

# 通过对象读取配置文件内容
secs = cf.sections() 
print( 'sections:', secs )

opts = cf.options("sec_a") 
print( 'options:', opts )

kvs = cf.items("sec_a") 
print( 'sec_a:', kvs )

str_val = cf.get("sec_a", "a_key1")  # 获取的值是str类型
int_val = cf.getint("sec_a", "a_key2")  # 获取的值是int类型
print( "value for sec_a's a_key1:", str_val )
print( "value for sec_a's a_key2:", int_val )

# 写配置文件
# 修改值
cf.set("sec_b", "b_key3", "new-$r") 
cf.set("sec_b", "b_newkey", "new-value")

# 创建一个新的section（如果section已经存在，则会报错）
cf.add_section('a_new_section')
# 新增 (option, value)
cf.set('a_new_section', 'new_key', 'new_value')

# 将对象写入到配置文件中
cf.write(open("./data/test.conf", "w"))