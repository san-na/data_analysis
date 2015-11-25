#coding:utf-8
'''
从贵州师范大学学生管理系统爬取全校学生相关信息

'''
import requests
import json
from datetime import datetime
from pymongo import MongoClient


'''连接到mongodb数据库'''
# 使用默认链接
client = MongoClient()
# 数据库名为gznu_all_student_info
db = client.gznu_all_student_info
# 数据库中相关表记录

# 学院相关信息
college_collection = db.college
# 班级相关信息
class_collection = db.class_
all_class_collection = db.all_class
# 学生信息
students_collection = db.students


def get_info(url, method='get'):
    '''获取信息'''
    cookies = {'JSESSIONID':'B14B2536404FA19AAD10E909677CB1A2'}
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'}
    if method == 'get':
        r = requests.get(url, cookies=cookies, headers=headers)
    else:
        r = requests.post(url, cookies=cookies, headers=headers)
    # 判断cookies是否失效
    failure_sign = u'\u8bf7\u91cd\u65b0\u767b\u5f55!!!'
    if failure_sign in r.text:
        print 'cookies 失效'
        return -1
    return r.text


def get_all_college_code():
    '''获取所有学院代码'''
    url = 'http://xgbfwq.gznu.edu.cn:8888/student/jsp/instructor/department_findSchoolComb.do?_dc=1447894809183'
    info = get_info(url, 'post')
    # 获取成功则将获取数据保持到数据库
    if info != -1:
        for i in json.loads(info[info.index('['):-1]):
            i['type'] = 'college_code'
            i['update'] = datetime.now()
            college_collection.insert(i)
        return True
    return False



def get_class_by_collection(college_code=''):
    '''通过学院代码获取该学院班级信息,
        若不传入学院代码，缺省获取所有学院班级信息
    '''
    uri = 'http://xgbfwq.gznu.edu.cn:8888/student/jsp/instructor/class_findClassTreeByLoginByXY.do?I_B_id={}'
    if college_code:
        url = uri.format(college_code)
    else:
        for i in college_collection.find({'type':'college_code'}):
            college_code = i['value']
            url = uri.format(college_code)
            _save_class_code(url, college_code)

def _save_class_code(url, college_code):
    '''将班级信息保持到数据库中'''

    print '[*] 正在将班级{}信息保存到数据库中'.format(college_code)
    info = get_info(url)
    for i in json.loads(info):
        for j in i['children']:
            item = {}
            item['class_code'] = j['id']
            item['text'] = j['text']
            item['college_code'] = college_code
            item['update'] = datetime.now()
            class_collection.insert(item)


def save_all_class():
    '''保存学校所有班级信息'''
    url = 'http://xgbfwq.gznu.edu.cn:8888/student/jsp/instructor/class_findAllclassConb.do?_dc=1447894809114'
    info = get_info(url)
    for i in json.loads(info[info.index('['):-1]):
        i['update'] = datetime.now()
        all_class_collection.insert(i)

def get_student_info(college_code='', class_code=''):
    '''获取学生信息'''
    print '[-] 开始获取学生信息'
    count  =0
    uri = 'http://xgbfwq.gznu.edu.cn:8888/student/jsp/instructor/mailist_findPageStudentByXY.do?C_id={}&limit=3000&start=0'
    for i in class_collection.find({'college_code':'90700'}):
        url = uri.format(i['class_code'])
        info = get_info(url, 'post')
        if info:
            count += 1
            print count
        else:
            print 'False'
        for i in json.loads(info[info.index('['):-1]):
            students_collection.insert(i)

if __name__ == '__main__':
    if get_all_college_code():
        print '[OK] 已将所有学院代码保持到数据库'
        get_class_by_collection()
        save_all_class()
        get_student_info()
    else:
        print '[-] 获取学院代码失败'
