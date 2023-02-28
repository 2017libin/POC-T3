import thirdparty.subDomainsBrute.subDomainsBrute as subDomainsBrute
import plugin.nowaf as nowaf
import os

# 定义get_targets函数，返回的是一个包含targets的列表
def get_targets():    
    output_file_list = []
    # 读取 domain_file 中的每一个域名来求出子域名
    for line in open(conf.INPUT_DOMAIN_FILE_PATH):
        sub = line.strip()
        if sub:
            # 创建临时文件存放结果
            root_path = os.path.dirname(os.path.abspath(__file__))
            tmp_dir = os.path.join(root_path, 'tmp')
            output_file = os.path.join(tmp_dir, f'{sub}_subdomains.txt')
            output_file_list.append(output_file)
            
            # 如果不存在文件夹则新建
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            
            # 如果已存在文件则删除（bushi）
            # 直接使用历史的查询结果
            if os.path.exists(output_file):
                continue
                # os.remove(tmp_file)
            
            # 设置枚举子域名的相关选项
            options = subDomainsBrute.Optios()
            options.no_cert_check = True
            options.output = output_file
            
            subDomainsBrute.subDomainsBrute(sub, options=options)
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
        th.queue.put(str(subdomains))
    
    # 过滤出没有waf的子域名？可访问的域名？
    th.queue = nowaf.nowaf_multithread(th.queue)
    
    # print(f"size of th.queue is {th.queue.qsize()}")
    # while not th.queue.empty():
    #     print(th.queue.get())
    
    # 调试信息
    # print(all_subdomains)
    # sys.exit(logger.info("exited by aoaoao"))