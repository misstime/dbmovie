# dbmovie
初学python，不使用任何框架的情况下抓取豆瓣电影，用以熟悉python。

环境
----------------------

我的环境：

~~~
# python
python 3.6.4
pymysql 0.9.1
lxml 4.1.1
request 2.18.4

# mysql
mysql 8.0.11
~~~

使用
---
1. 一条命令（不推荐）：先抓取列表，再抓取详情
~~~
python cmd.py --type=all
~~~

2. 两条命令（推荐）：分别分开抓取列表、详情；
~~~
# 这样方便自由的配置定时执行
python cmd.py --type=list
python cmd.py --tpye=info
~~~

#### notice：

项目需提前配置log目录、页面存储目录，参考`config.py` -- `spider_cfg`、`log_cfg`

数据已保存至网盘：[约4.5万条数据](http://xxxx.com)

数据库
--------

#### subject

~~~
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for subject
-- ----------------------------
DROP TABLE IF EXISTS `subject`;
CREATE TABLE `subject` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `did` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '条目id',
  `subtype` int(1) unsigned NOT NULL DEFAULT '0' COMMENT '条目分类',
  `imdb` varchar(20) NOT NULL DEFAULT '' COMMENT 'IMDb',
  `title` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '中文名',
  `original_title` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '原名',
  `aka` varchar(2000) NOT NULL DEFAULT '' COMMENT '又名',
  `rating` varchar(4) NOT NULL DEFAULT '' COMMENT '评分',
  `star` varchar(255) NOT NULL DEFAULT '' COMMENT '各星比例',
  `ratings_count` int(10) unsigned DEFAULT NULL COMMENT '评分人数',
  `wish_count` int(10) unsigned DEFAULT NULL COMMENT '想看人数',
  `collect_count` int(10) unsigned DEFAULT NULL COMMENT '看过人数',
  `comments_count` int(10) unsigned DEFAULT NULL COMMENT '短评数量',
  `reviews_count` int(10) DEFAULT NULL COMMENT '影评数量',
  `year` varchar(4) NOT NULL DEFAULT '' COMMENT '年代',
  `languages` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '语言',
  `countries` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '制片国家/地区',
  `pubdates` varchar(500) NOT NULL DEFAULT '' COMMENT '上映日期',
  `directors` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '导演',
  `casts` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '主演',
  `writers` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '编剧',
  `genres` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '影片类型',
  `tags` varchar(500) NOT NULL DEFAULT '' COMMENT '豆瓣成员常用标签',
  `website` varchar(255) NOT NULL DEFAULT '' COMMENT '官方网站',
  `douban_site` varchar(255) NOT NULL DEFAULT '' COMMENT '豆瓣小站',
  `durations` varchar(255) NOT NULL DEFAULT '' COMMENT '片长',
  `cover` varchar(255) NOT NULL DEFAULT '' COMMENT '电影海报图',
  `summary` text,
  `info_updated` tinyint(1) NOT NULL DEFAULT '0' COMMENT '详情页是否已抓取更新（-1：页面不存在，0：默认，1：已更新）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `did` (`did`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='影视条目表';
~~~











