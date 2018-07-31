import logging
import json
import re
import time
from lxml import etree

from spider.spider import Spider
from spider.db import db

class Info(Spider):
    '''抓取电影条目详情'''

    def __init__(self, cmd_cfg):
        super(Info, self).__init__(cmd_cfg)
        self.url_prefix = 'https://movie.douban.com/subject/'
        self.init_logging(cmd_cfg)          # 配置logging
        self.log = logging.getLogger('spider.info')
        self.subjects = set()               # 所有待更新条目
        self.batch_data = []                # 批次待更新数据
        self.re = {
            'h1':re.compile(r'<h1>(.+?)</h1>', re.S),
            'xxx':re.compile(r'xxx', re.S),
        }

    def run(self):
        self.subjects = self.getAllSubject()
        start = 0
        while self.subjects[start:start+self.batch_num]:
            self.batch_data = []
            batch = self.subjects[start:start+self.batch_num]
            batch = list(map(lambda x: {'name':x['did'], 'url':self.url_prefix + str(x['did']) + '/', 'data':x}, batch))
            threads = self.multiThreading(batch)    # 将批次添加至多线程
            self.startThreads(threads)              # 执行多线程
            self.saveData(self.batch_data)          # 数据入库更新
            self.log.info(f"id: {self.subjects[start]['id']}-{self.subjects[start + self.batch_num - 1]['id']} 更新：{len(self.batch_data)}/{self.batch_num}条")
            start += self.batch_num
        self.log.info('over')

    def crawl(self, url, did, thread_info):
        '''抓取页面、处理数据'''
        html = self.fetch(url)
        self.saveHtml(html, 'info', did)
        data = self.parseHtml(html, thread_info)
        if data:
            self.subjects_lock.acquire()
            self.batch_data.append({'data':data, 'thread_info':thread_info})
            self.subjects_lock.release()

    def parseHtml(self, html, thread_info):
        '''解析html，提炼数据'''
        id = thread_info['id']
        did = thread_info['did']
        title = thread_info['title']
        data = {
            'subtype':'1',
            'imdb':'',
            'original_title':'',
            'aka':'',
            'rating':'',
            'star':'',
            'ratings_count':'0',
            'wish_count':'0',
            'collect_count':'0',
            'comments_count':'0',
            'reviews_count':'0',
            'year':'',
            'languages':'',
            'countries':'',
            'pubdates':'',
            'directors':'',
            'casts':'',
            'writers':'',
            'genres':'',
            'website':'',
            'douban_site':'',
            'durations':'',
            'cover':'',
            'summary':'',
            'info_updated':'1',
            'tags':'',
        }

        tree = etree.HTML(html)

        # imdb aka languages countries pubdates directors casts writers genres website douban_site durations
        info_div = tree.xpath('//div[@id="info"]')
        if not info_div:
            tmp = tree.xpath('//title/text()')
            if tmp:
                if tmp[0] == '页面不存在':
                    self.log.warning(f'{did} {title} -- 页面不存在')
                    return {'info_updated':'-1'}
            else:
                self.log.warning(f'{did} {title} -- xpath failed: info_div 疑似错误页面')
                return None
        else:
            # casts
            block = info_div[0].xpath('//span[contains(text(), "主演")]/parent::span/span/a')
            items = []
            if block:
                for a in block:
                    tmp = re.search(r'/celebrity/(\d+)?/', a.attrib.get('href'))
                    if tmp:
                        cel_num = tmp[1]
                    else:
                        cel_num = '0'
                    cel_name = a.text.strip()
                    items.append({cel_num:cel_name})
                if items:
                    data['casts'] = json.dumps(items)
            else:
                self.log.warning(f'{did} {title} -- xpath failed: casts')

            # writers
            block = info_div[0].xpath('//span[contains(text(), "编剧")]/parent::span/span/a')
            items = []
            if block:
                for a in block:
                    tmp = re.search(r'/celebrity/(\d+)?/', a.attrib.get('href'))
                    if tmp:
                        cel_num = tmp[1]
                    else:
                        cel_num = '0'
                    cel_name = a.text.strip()
                    items.append({cel_num: cel_name})
                if items:
                    data['writers'] = json.dumps(items)
            else:
                self.log.warning(f'{did} {title} -- xpath failed: writers')

            # directors
            block = info_div[0].xpath('//span[contains(text(), "导演")]/parent::span/span/a')
            items = []
            if block:
                for a in block:
                    tmp = re.search(r'/celebrity/(\d+)?/', a.attrib.get('href'))
                    if tmp:
                        cel_num = tmp[1]
                    else:
                        cel_num = '0'
                    cel_name = a.text.strip()
                    items.append({cel_num: cel_name})
                if items:
                    data['directors'] = json.dumps(items)
            else:
                self.log.warning(f'{did} {title} -- xpath failed: directors')

            # genres
            tmp = info_div[0].xpath('//span[@property="v:genre"]/text()')
            if tmp:
                data['genres'] = json.dumps(tmp)
            else:
                self.log.warning(f'{did} {title} -- xpath failed: genres')

            # pubdates
            tmp = info_div[0].xpath('//span[@property="v:initialReleaseDate"]/text()')
            if tmp:
                data['pubdates'] = json.dumps(tmp)
            else:
                self.log.warning(f'{did} {title} -- xpath failed: pubdates')

            # durations
            tmp = info_div[0].xpath('//span[@property="v:runtime"]/text()')
            if tmp:
                data['durations'] = tmp[0]
            else:
                self.log.warning(f'{did} {title} -- xpath failed: durations')

            # imdb
            tmp = info_div[0].xpath('//span[contains(text(), "IMDb链接:")]/following::a[1]/text()')
            if tmp:
                data['imdb'] = tmp[0]
            else:
                self.log.warning(f'{did} {title} -- xpath failed: imdb')

            # website
            tmp = info_div[0].xpath('//span[contains(text(), "官方网站:")]/following::a[1]/text()')
            if tmp:
                data['website'] = tmp[0]
            else:
                pass

            # douban_site
            tmp = info_div[0].xpath('//span[contains(text(), "官方小站:")]/following::a[1]')
            if tmp:
                ds_name = tmp[0].text
                ds_num = tmp[0].attrib.get('href').replace('https://site.douban.com/', '').strip('/')
                data['douban_site'] = json.dumps({ds_num: ds_name})
            else:
                pass

            # aka languages countries
            self.re = {
                'info_div':re.compile(r'<div id="info">(.+?)</div>', re.S),
                'aka':re.compile(r'又名:</span>(.+?)<br/>', re.S),
                'languages':re.compile(r'语言:</span>(.+?)<br/>', re.S),
                'countries':re.compile(r'制片国家/地区:</span>(.+?)<br/>', re.S),
                'durations':re.compile(r'片长:</span>(.+?)<br/>', re.S),
            }
            tmp = self.re['info_div'].search(html)
            if tmp:
                # aka
                tmp1 = self.re['aka'].search(tmp[1])
                if tmp1:
                    tmp2 = tmp1[1].strip().split(' / ')
                    if tmp2:
                        data['aka'] = json.dumps(tmp2)
                    else:
                        self.log.warning(f'{did} {title} -- regex failed: aka')
                # languages
                tmp1 = self.re['languages'].search(tmp[1])
                if tmp1:
                    tmp2 = tmp1[1].strip().split(' / ')
                    if tmp2:
                        data['languages'] = json.dumps(tmp2)
                    else:
                        self.log.warning(f'{did} {title} -- regex failed: languages')
                # countries
                tmp1 = self.re['countries'].search(tmp[1])
                if tmp1:
                    tmp2 = tmp1[1].strip().split(' / ')
                    if tmp2:
                        data['countries'] = json.dumps(tmp2)
                    else:
                        self.log.warning(f'{did} {title} -- regex failed: countries')

        # original_title year
        h1 = tree.xpath('//h1')
        if h1:
            complex_title = h1[0].xpath('span[1]/text()')
            if complex_title:
                tmp = complex_title[0].strip().replace(title, '').strip()
                if tmp:
                    data['original_title'] = tmp
                else:
                    data['original_title'] = title
            else:
                self.log.warning(f'{did} {title} -- xpath failed: complex_title')
            tmp = h1[0].xpath('span[2]/text()')
            if tmp:
                data['year'] = tmp[0].lstrip('(').rstrip(')')

        # rating star ratings_count
        rating_div = tree.xpath('//div[@id="interest_sectl"]')
        if rating_div:
            # rating
            rating = rating_div[0].xpath('//strong[@property="v:average"]/text()')
            if rating:
                data['rating'] = rating[0].strip()
            else:
                self.log.warning(f'{did} {title} -- xpath failed: rating')
            # ratings_count
            ratings_count = rating_div[0].xpath('//span[@property="v:votes"]/text()')
            if ratings_count:
                data['ratings_count'] = ratings_count[0].strip()
            else:
                self.log.warning(f'{did} {title} -- xpath failed: ratings_count')
            # star
            star = rating_div[0].xpath('//span[@class="rating_per"]/text()')
            if star:
                data['star'] = json.dumps(star)
            else:
                self.log.warning(f'{did} {title} -- xpath failed: star')
        else:
            self.log.warning(f'{did} {title} -- xpath failed: rating_div')

        # wish_count collect_count
        tmp = tree.xpath('//div[@class="subject-others-interests-ft"]/a/text()')
        if tmp:
            data['collect_count'] = tmp[0].strip().replace('人看过', '')
            data['wish_count'] = tmp[1].strip().replace('人想看', '')
        else:
            self.log.warning(f'{did} {title} -- xpath failed: wish_count collect_count')

        # tags
        tmp = tree.xpath('//div[@class="tags-body"]/a/text()')
        if tmp:
            data['tags'] = json.dumps(tmp)
        else:
            self.log.warning(f'{did} {title} -- xpath failed: tags')

        # cover
        tmp = tree.xpath('//div[@id="mainpic"]/a/img/@src')
        if tmp:
            data['cover'] = tmp[0]
        else:
            self.log.warning(f'{did} {title} -- xpath failed: cover')

        # summary
        tmp = tree.xpath('//span[@class="all hidden"]/text()')
        if tmp:
            tmp = map(lambda x: x.strip(), tmp)
            data['summary'] = json.dumps(list(tmp))
        else:
            tmp1 = tree.xpath('//span[@property="v:summary"]/text()')
            if tmp1:
                tmp1 = map(lambda x: x.strip(), tmp1)
                data['summary'] = json.dumps(list(tmp1))
            else:
                self.log.warning(f'{did} {title} -- xpath failed: summary')

        # comments_count
        tmp = tree.xpath('//h2/i[contains(text(), "的短评")]/parent::h2/span/a/text()')
        if tmp:
            data['comments_count'] = tmp[0].strip('全部 ').strip(' 条')
        else:
            self.log.warning(f'{did} {title} -- xpath failed: comments_count')

        # reviews_count
        tmp = tree.xpath('//h2[contains(text(), "的影评")]/span/a/text()')
        if tmp:
            data['reviews_count'] = tmp[0].strip('全部 ').strip(' 条')
        else:
            self.log.warning(f'{did} {title} -- xpath failed: reviews_count')

        return data

    def getAllSubject(self):
        '''获取所有待更新条目'''
        sql = "SELECT `id`, `did`, `title` FROM `subject` WHERE `info_updated`=0 ORDER BY `id` ASC;"
        return db.fetchall(sql)

    def saveData(self, batch_data):
        '''更新数据'''
        if not batch_data:
            self.log.warning(f'batch_data empty!')
            return
        for subject in batch_data:
            args = []
            items = []
            sql_prefix = 'UPDATE `subject` SET '
            sql_suffix = " WHERE `id`='%s'"

            for k, v in subject['data'].items():
                items.append(f"`{k}`=%s")
                args.append(v)
            sql = sql_prefix + ', '.join(items) + sql_suffix
            args.append(subject['thread_info']['id'])
            try:
                db.execute(sql, args)
            except Exception as e:
                self.log.warning(f"db update failed -- {subject['thread_info']['id']} {subject['thread_info']['did']} {subject['thread_info']['title']}")
                self.log.warning(f'--> {e}')

















