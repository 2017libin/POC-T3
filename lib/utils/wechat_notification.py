import requests
from lib.utils.config import ConfigFileParser

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        ret = ""
        for line in f.readlines():
            # 每行之间空出一个行才能保证正确换行
            ret = ret + f"{line}\n"
        print(ret)
        return ret

def notification(text, desp):
    url = f"https://sctapi.ftqq.com/{ConfigFileParser().ServerJiangSendKey()}.send"
    data = {
        'text': text,
        'desp': desp
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    notification('测试', read_file('README.md'))