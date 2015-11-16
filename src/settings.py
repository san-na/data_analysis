# coding: utf-8

__author__ = 'laymen'
__date__ = '2015-11-14'


DEBUG = True

DB_CONFID = dict(
        host='localhost',
        user='root',
        db = 'data_analysis',
        charset='utf8',
        )

SQLALCHEMY_DATABASE_URL = 'mysql://%s:%s@%s%s?charset=%s' % (
        DB_CONFID['user'],
        DB_CONFID['passwd'],
        DB_CONFID['host'],
        DB_CONFID['db'],
        DB_CONFID['charset'],
        )
