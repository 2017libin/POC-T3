import requests

def read_txt(path):
    '''
    读取文件
    '''
    with open(path, 'r', encoding='utf-8') as f:
        ret = ""
        for line in f.readlines():
            # 每行之间空出一个行才能保证正确换行
            ret = ret + f"{line}\n"
        print(ret)
        return ret

def wechat_notification(text, desp):
    '''
    发送消息
    '''
    url = 'https://sctapi.ftqq.com/SCT198871T4ADz2BgDgHq2WkHvTu72yWwf.send'
    data = {
        'text': text,
        'desp': desp
    }
    requests.post(url, data=data)

wechat_notification('测试', read_txt('README.md'))