'''
    360 quake搜索引擎
'''
import optparse
import datetime
import math
import time
import requests


# 对列表进行去重
def remove_dup(get_list):
    return list(set(get_list))

class Quake360Cn:
    def __init__(self, key):
        self.key = key
        self.href = 'https://quake.360.cn/'
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46"
        self.url_list = list()
        self.domain_list = list()
        self.ip_list = list()

    def get_one_year_range(self):
        this_time = time.localtime()
        year = this_time.tm_year
        mon = this_time.tm_mon
        day = this_time.tm_mday
        hour = this_time.tm_hour
        min = this_time.tm_min
        sec = this_time.tm_sec
        this_time = f'{year}-{mon}-{day} {hour}:{min}:{sec}'
        this_date = datetime.datetime.strptime(this_time, '%Y-%m-%d %H:%M:%S')
        # print(this_date)
        _u = datetime.timedelta(days=365)
        self.start_time = str(this_date - _u)
        self.end_time = str(this_date)
        # print(start_time, end_time)

    def check_req(self, key=None):
        try:
            if self.key == '' and not key:
                return False
            if key:
                this_key = key
            else:
                this_key = self.key
            self.get_one_year_range()
            headers = {
                "X-QuakeToken": this_key,
                "Content-Type": "application/json",
                "user-Agent": self.ua
            }
            # domain:"baidu.com"
            data = {
                "query": f'domain:"xxx.com"',
                "start": 0,
                "size": 10,
                "ignore_cache": False,
                "start_time": self.start_time,
                "end_time": self.end_time
            }
            requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=headers, timeout=18, json=data).json()
            return True
        except Exception as e:
            print(e)
            return False

    def start_search(self, query_str):
        try:
            if self.key == '':
                return False
            self.get_one_year_range()
            headers = {
                "X-QuakeToken": self.key,
                "Content-Type": "application/json",
                "user-Agent": self.ua
            }
            # domain:"baidu.com"
            data = {
                "query": query_str,
                "start": 0,
                "size": 100,
                "ignore_cache": False,
                "start_time": self.start_time,
                "end_time": self.end_time
            }
            req = requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=headers, timeout=18, json=data)
            get_json = req.json()
            # pprint.pprint(get_json)
            total = get_json['meta']['pagination']['total']
            print('[Quake360Cn] total===>', total)
            for site in get_json['data']:
                self.add_append_url(site=site)

            # site_list = remove_dup(site_list)
            # print('[Quake360Cn]',len(site_list),site_list)
            pages = math.ceil(total/100)
            if pages > 1:
                for page in range(1, pages+1):
                    time.sleep(1)
                    print('[Quake360Cn] page===>', page+1)
                    data = {
                        "query": query_str,
                        "start": page*100,
                        "size": 100,
                        "ignore_cache": False,
                        "start_time": self.start_time,
                        "end_time": self.end_time
                    }
                    # print(data)
                    req = requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=headers,timeout=380, json=data)
                    get_json = req.json()
                    if not get_json['data']:
                        break
                    for site in get_json['data']:
                        # print(site.keys())
                        self.add_append_url(site=site)
                    # print(len(site_list), site_list)
                    # if page == 3:   # 测试用
                    #     break

            # 保存结果
            self.save_result_domain(self.domain_list)
            self.save_result_ips(self.ip_list)
            self.save_result_url(self.url_list)
            return True
            # return {'domains': site_list, 'ips': []}
        except Exception as e:
            print(f'[Quake360Cn - 子域名查询] {e.args} ')
            return False

    def add_append_url(self, site):
        # domain_list = []
        # ip_list = []
        port = site['port']
        if 'domain' in list(site.keys()):
            if port == 443:
                url = f'https://{site["domain"]}:{port}'
            else:
                url = f'http://{site["domain"]}:{port}'
            self.url_list.append(url)
            self.domain_list.append(site["domain"])
        else:
            if port == 443:
                url = f'https://{site["ip"]}:{port}'
            else:
                url = f'http://{site["ip"]}:{port}'
            self.url_list.append(url)
            self.ip_list.append(site["ip"])
        print(url)
        return True

    def save_result_url(self, url_list):
        """
            保存域名文件/url.txt
        """
        url_list = remove_dup(url_list)
        print(len(url_list), 'url_list')
        with open('url.txt','w+',encoding='utf-8') as f:
            f.write('\n'.join(url_list))
        print('[+] URL保存成功')

    def save_result_domain(self, domain_list):
        """
            保存域名文件/domain.txt
        """
        domain_list = remove_dup(domain_list)
        print(len(domain_list), 'domain_list')
        with open('domain.txt','w+',encoding='utf-8') as f:
            f.write('\n'.join(domain_list))
        print('[+] Domain保存成功')

    def save_result_ips(self, ip_list):
        """
            保存域名文件/ips.txt
        """
        ip_list = remove_dup(ip_list)
        print(len(ip_list), 'ip_list')
        with open('ips.txt','w+',encoding='utf-8') as f:
            f.write('\n'.join(ip_list))
        print('[+] IP保存成功')


def echo_log():
    log = '''
 _____  ____ _____  _____             _        
|____ |/ ___|  _  ||  _  |           | |       
    / / /___| |/' || | | |_   _  __ _| | _____ 
    \ \ ___ \  /| || | | | | | |/ _` | |/ / _ \\
.___/ / \_/ \ |_/ /\ \/' / |_| | (_| |   <  __/
\____/\_____/\___/  \_/\_\\__,_|\__,_|_|\_\___|
                                               
                                               
'''
    print(log)


if __name__ == "__main__":
    echo_log()
    usage = '"usage:python3 %prog -k/--key -q/--query ","version = 1.0.1"'
    parse = optparse.OptionParser(usage)
    parse.add_option("-k", "--key", dest="Key", type=str, help="Enter the key to be detected")
    parse.add_option("-q", "--query", dest="Query", type=str, help="Enter the query to be detected")
    parse.add_option("-v", help="software version")
    options, args = parse.parse_args()
    if options.Key != None and options.Query != None:
        # query_str = 'app:"ThinkPHP" and country:"China"'
        query_str = options.Query
        key = options.Key
        print(f'[*][Key] {key}')
        print(f'[*][Query] {query_str}')
        get_resu = Quake360Cn(key=key).start_search(query_str=query_str)
    else:
        print("\nExample: python3 main.py -k dadds -q 'app:\"ThinkPHP\" and country:\"China\"'\n")

# 654425dd-0411-4fd4-a43b-97c5439922cb