import pymysql
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import  datetime
import random
from functools import wraps
from flask import (session,redirect,url_for)
from  views.index_bp import *


from utils import config
pymysql.install_as_MySQLdb()

engine = create_engine(
    'mysql://' + config.USER + ':' + config.PASSWORD + '@' + config.HOST + '/' + config.DB_NAME + '?charset=utf8mb4')
metadata = MetaData(bind=engine)
conn = engine.connect()


met_login_details = Table("login_details", metadata, autoload=True)
met_emp_personal_details = Table("EMP_PERSONAL_DETAILS", metadata, autoload=True)
met_attendance_management = Table("attendance_management", metadata, autoload=True)
met_doc_vault = Table("doc_vault", metadata, autoload=True)
met_leaves_application = Table("leaves_application", metadata, autoload=True)
met_salary_statement = Table("salary_statement", metadata, autoload=True)

def executeRawQueryAll(query):
    Session = sessionmaker(bind=engine)
    session = Session()
    res = session.execute(query).fetchall()
    session.close()
    return res


def fetchAllKeyValuePair(res):
    d, data = {}, []
    for val in res:
        for column, value in val.items():
            d = {**d, **{column: value}}
        data.append(d)

    return data


def genSequenceId(val):

    base_date = str(datetime.datetime.now().strftime('%y%m%d'))
    print(base_date,'base_date')
    random_number=random.randint(1000,5000)
    base = base_date + str(random_number)
    print(base,'base')

    emp_id = val + base
    return emp_id

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            return f(*args, **kwargs)
        else:
            return redirect('/index')

    return wrap

