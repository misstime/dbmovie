import json
import logging

from spider.spider import Spider
from spider.db import db

class List(Spider):
    '''批量抓取/更新电影列表页'''

    def __init__(self, cmd_cfg):
        super(List, self).__init__(cmd_cfg)
        self.url_prefix = 'https://movie.douban.com/j/new_search_subjects?sort=R&range=0,10'
        self.init_logging(cmd_cfg)          # 配置logging
        self.log = logging.getLogger('spider.list')
        self.subjects = set()               # 已入库所有条目
        self.new_subject = []               # 当前批次待入库条目

    def run(self):
        '''入口函数，控制抓取流程，分批次抓取'''
        self.subjects = self.getAllSubject()
        all_tags = self.getTags()
        for tags in all_tags:
            cur_page = 0
            self.is_over = False
            while not self.is_over:     # 每个类别/tags抓取到没有返回数据为止
                # 批次
                self.new_subject = []
                batch = []
                page_list = range(cur_page, cur_page + self.batch_num * 20, 20)
                for start in page_list:
                    item = {}
                    item['url'] = f'{self.url_prefix}&tags={tags[0]}&genres={tags[1]}&countries={tags[2]}&start={start}'
                    item['name'] = f'{tags[0]}-{tags[1]}-{tags[2]}-{start}'
                    item['data'] = {}
                    batch.append(item)
                threads = self.multiThreading(batch)    # 将批次添加至多线程
                self.startThreads(threads)              # 执行多线程
                self.saveBatch()                        # 批次数据入库
                self.logBatch(cur_page, cur_page + self.batch_num * 20, tags)      # 记录批次
                cur_page += self.batch_num * 20
        self.log.info('over')

    def crawl(self, url, page_name, data):
        '''抓取页面、整理数据，待入库'''
        html = self.fetch(url)
        self.manageHtml(html, 'list', page_name)         # 保存页面
        data = json.loads(html)['data']
        self.subjects_lock.acquire()
        if not data:
            if not self.is_over:
                self.log.info('当前tags抓取完毕，data empty')
            self.is_over = True
        else:
            for item in data:
                did = int(item['id'])
                if did in self.subjects:
                    pass
                else:
                    self.subjects.add(did)
                    self.new_subject.append(item)
        self.subjects_lock.release()

    def saveBatch(self):
        '''入库每个批次的新数据'''
        if self.new_subject:
            sql_prefix = "INSERT INTO `subject` (`did`, `title`) VALUES "
            values = []
            args = []
            for sub in self.new_subject:
                values.append("(%s, %s)")
                args.append(sub['id'])
                args.append(sub['title'])
            sql = sql_prefix + ', '.join(values) + ';'
            res = db.execute(sql, args)
            return res
        else:
            return 0

    def getAllSubject(self):
        '''获取所有条目，供去重使用'''
        subjects = set()
        sql = "SELECT `did` FROM `subject`"
        res = db.fetchall(sql)
        for item in res:
            subjects.add(item['did'])
        return subjects

    def getTags(self):
        '''获取所有电影tag'''
        cat = ['电影']
        type = ['剧情', '喜剧', '动作', '爱情', '科幻', '悬疑', '惊悚', '恐怖', '犯罪', '同性', '音乐', '歌舞', '传记',
                '历史', '战争', '西部', '奇幻', '冒险', '灾难', '武侠', '情色']
        area = ['中国大陆', '美国', '香港', '台湾', '日本', '韩国', '英国', '法国', '德国', '意大利', '西班牙', '印度',
                '泰国', '俄罗斯', '伊朗', '加拿大', '澳大利亚', '爱尔兰', '瑞典', '巴西', '丹麦']

        tags = []
        for c in cat:
            for t in type:
                for a in area:
                    tags.append([c, t, a])
        return tags

    def logBatch(self, start_num, end_num, tags):
        '''记录批次抓取'''
        log_str = f'batch: {tags[0]}-{tags[1]}-{tags[2]}-{start_num}-{end_num} , new subjects： {len(self.new_subject)}'
        self.log.info(log_str)



