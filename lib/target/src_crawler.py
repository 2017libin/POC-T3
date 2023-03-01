import thirdparty.subDomainsBrute.subDomainsBrute as subDomainsBrute
import plugin.nowaf as nowaf
import os
import queue

# 需要扫描的子域名
domain_list = ["lixiang.com", "chehejia.com"]

# 定义get_targets函数，返回的是一个包含targets的列表
def get_targets(use_cache = True):
    output_file_list = []
    targets_queue = queue.Queue()
    
    # 创建临时文件存放结果
    root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(root_path, 'subDomainsBrute_output')
    
    # 如果不存在文件夹则新建
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    # 1. 获取子域名
    for domain in domain_list:
        output_file = os.path.join(tmp_dir, f'{domain}_subdomains.txt')
        output_file_list.append(output_file)
        
        if os.path.exists(output_file):
            # 是否使用历史的查询结果
            if use_cache:
                continue
            # os.remove(tmp_file)
        
        # 使用 subDomainsBrute 获取子域名
        # 设置枚举子域名的相关选项
        options = subDomainsBrute.Optios()
        options.no_cert_check = True
        options.output = output_file
        subDomainsBrute.subDomainsBrute(domain, options=options)
        # sys.exit(logger.info("exited by aoaoao"))
    
    # 将所有的扫描结果放入集合进行去重
    all_subdomains = set()
    for _file in output_file_list:
        with open(_file, 'r') as tmp_f:
            for domain in tmp_f:
                domain = domain.split()[0]
                if domain not in all_subdomains:
                    all_subdomains.add(domain)       # cname query can result in duplicated domains
    
    # 将过滤后的子域名加入队列作为测试目标
    for subdomains in all_subdomains:   
        targets_queue.put(str(subdomains))
    
    # 过滤出没有waf的子域名？可访问的域名？
    targets_queue = nowaf.nowaf_multithread(targets_queue)
    
    # 爬虫
    # ...
    
    # print(f"Getted {targets_queue.qsize()} targets")
    # while not targets_queue.empty():
    #     print(targets_queue.get())
    
    return list(targets_queue.queue)
    # 调试信息
    # print(all_subdomains)
    # sys.exit(logger.info("exited by aoaoao"))