import shodan
v

# 直接手动修改配置文件会更方便写。。。，这段代码仅用于学习
# #shodan接口处理函数
# def shodan_apikey_write(Key):
#     config = ConfigParser()

#     # 如果不存在shodan section
#     if 'shodan' not in config.sections():
#         config.add_section('shodan')
    
#     # 修改或者新建shodan KEY
#     config['shodan']['KEY'] = Key
    
#     # 将修改的内容写回文件
#     with open('./api.conf','w') as configFile:
#         config.write(configFile)

def shodan_apikey_read():
    config = ConfigParser()
    config.read('./api.conf')
    KEY = config['shodan']["KEY"]
    return KEY

def test_search():
    SHODAN_API_KEY = shodan_apikey_read()
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        results = api.search('Apache')
        print( 'Results found: %s' % results['total'])
        for result in results['matches']:         
                print ("%s:%s|%s|%s"%(result['ip_str'],result['port'],result['location']['country_name'],result['hostnames']))
    except shodan.APIError as e:
        print( 'Error: %s' % e)

if __name__ == '__main__':
    test_search()