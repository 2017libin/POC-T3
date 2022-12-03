import zoomeye.sdk as zoomeye
from configparser import ConfigParser

def zoomeye_apikey_read():
    config = ConfigParser()
    config.read('./api.conf')
    
    key = config['zoomeye']["key"]

    return key

def test_search():
    zm = zoomeye.ZoomEye(api_key=zoomeye_apikey_read())
    info = zm.resources_info()
    print(info)
    data = zm.dork_search('http city:guangzhou', page=1, resource='host')
    print(zm.dork_filter('ip,port'))

if __name__ == '__main__':
    test_search()