import string
import random
import requests
import threading
import time
import logging
import os

from config import *

class Spider(object):
    '''蜘蛛基类'''
    def __init__(self, cmd_cfg):
        self.cmd_cfg = cmd_cfg
        self.db_config = db_cfg

        self.batch_num = 20      # 每批次抓取页面个数
        self.is_over = False    # 当前条件下是否抓取完毕

        #self.origin_cookies = 'll="108288"; bid=8gGy20BFzSo; ap=1; _vwo_uuid_v2=DDCA62D0EED5D076AA5EF225CA70972BA|193ddaddd8ecda6a4ffa794c912a90aa; __utmz=30149280.1530082535.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _ga=GA1.2.1062266840.1530070679; _gid=GA1.2.2063798377.1531294856; push_noty_num=0; push_doumail_num=0; __utmv=30149280.6284; __utma=30149280.1062266840.1530070679.1531386939.1531442489.9; __utmc=30149280; dbcl2="62846626:lr9dxFssIOg"; ck=eMQI; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1531442501%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; __utma=223695111.119371641.1530070679.1531386939.1531442501.8; __utmc=223695111; __utmz=223695111.1531442501.8.6.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_id.100001.4cf6=022515c7220cfaf6.1530070679.8.1531442510.1531387230.'
        self.origin_cookies = 'bid=07MD-NV8FFY; ps=y; ll="108288"; __utma=30149280.424160577.1532503657.1532503657.1532503657.1; __utmc=30149280; __utmz=30149280.1532503657.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1532503659%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=223695111.1576156857.1532503659.1532503659.1532503659.1; __utmb=223695111.0.10.1532503659; __utmc=223695111; __utmz=223695111.1532503659.1.1.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt_t1=1; _vwo_uuid_v2=D545E20691B844CF0C4E59B9A7D78F388|7baa859c72b0d08e373bfc67062182ef; _pk_id.100001.4cf6=d403fad732216d5f.1532503659.1.1532503722.1532503659.; __utmb=30149280.14.8.1532503722378; RT=s=1532503786010&r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F26930056%2F%3Ffrom%3Dshowing'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'movie.douban.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        }

        self.subjects_lock = threading.Lock()    # 锁 -- 去重操作

    def manageHtml(self, data, subtype, page_name):
        '''根据命令，保存页面'''
        if self.cmd_cfg['saveHtml'] == 'yes':
            self.saveHtml(data, subtype, page_name)

    def saveHtml(self, data, subtype, page_name):
        '''保存页面到硬盘'''
        if subtype == 'list':
            path = spider_cfg['html_list_dir']
        elif subtype == 'info':
            path = spider_cfg['html_info_dir']

        if not os.path.exists(path):
            os.makedirs(path)

        if subtype == 'list':
            path += str(page_name) + '.json'
        elif subtype == 'info':
            path += str(page_name) + '.html'

        with open(path, mode='w', encoding="utf-8") as f:
            f.write(data)
            f.close()

    def init_logging(self, cmd_cfg):
        '''配置logging'''
        logger = logging.getLogger('spider')
        logger.setLevel(level=logging.DEBUG)

        log_file_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '_' + cmd_cfg['type']
        if not cmd_cfg['saveHtml']:
            log_file_name += '_unSaveHtml'
        if cmd_cfg['miss']:
            log_file_name += '_miss'

        handler = logging.FileHandler(log_cfg['log_dir'] + log_file_name + '.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        logger.addHandler(handler)
        logger.addHandler(console)

    def fetch(self, url):
        '''获取页面'''
        cookies = self.getCookie(self.origin_cookies)
        res = requests.get(url, headers=self.headers, cookies=cookies, allow_redirects=False)

        return res.text

    def getCookie(self, cookies):
        '''获取cookies'''
        cookies = cookies.split('; ')
        rtn = {}
        for cookie in cookies:
            item = cookie.split('=', 1)
            rtn[item[0]] = item[1]

        # 生成cookie的bid值，绕过豆瓣的反爬策略，详见：https://zhuanlan.zhihu.com/p/24035574
        bid = ''.join(random.sample(string.ascii_letters + string.digits, 11))
        rtn['bid'] = bid

        return rtn

    def multiThreading(self, batch):
        '''将批次添加至多线程'''
        threads = []
        for page in batch:
            thread = threading.Thread(target=self.crawl, name=page['name'], args=(page['url'], page['name'], page['data']))
            threads.append(thread)
        return threads

    def startThreads(self, threads):
        '''执行多线程'''
        import time
        for t in threads:
            t.start()   # 启动一个线程
        for t in threads:
            t.join()    # 等待每个线程执行结束