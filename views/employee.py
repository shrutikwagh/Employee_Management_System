import gc

from flask import (Blueprint, render_template, redirect, request, jsonify, url_for, flash)
from sqlalchemy import bindparam,update
from utils import db
from utils.db import *
from flask import session
from functools import wraps

employee = Blueprint("employee", __name__)


@employee.route('/AddPersonalDetails', methods=['POST', 'GET'])
@login_required
def add_personal_details():
    print(session)
    user_id=session['USER_ID']
    role=session['ROLE']
    user_name=session['FIRST_NAME']+" "+session['LAST_NAME']
    sql="SELECT * FROM login_details WHERE EMP_ID ='{}'".format(user_id)
    res=db.executeRawQueryAll(sql)
    login_details1=db.fetchAllKeyValuePair(res)
    if len(login_details1)>0:
        login_details=login_details1[0]
    else:
        login_details={}

    sql="SELECT * FROM emp_personal_details WHERE EMP_ID ='{}'".format(user_id)
    res=db.executeRawQueryAll(sql)
    emp_personal_details1=db.fetchAllKeyValuePair(res)
    if len(emp_personal_details1)>0:
        emp_personal_details=emp_personal_details1[0]
    else:
        emp_personal_details={}


    if 'logged_in' in session:
        if request.method=="POST":

            if len(emp_personal_details1) > 0:

                update_data = [{
                    "_EMP_ID": request.form.get('emp_id'),
                    "FIRST_NAME": request.form.get('first_name'),
                    "LAST_NAME": request.form.get('last_name'),
                    "ROLE": request.form.get('role'),
                    "EMAIL": request.form.get('email'),
                    "CONTACT_NO": request.form.get('contact_no'),
                    "CURRENT_ADDRESS": request.form.get('Current_address'),
                    "CURRENT_CITY": request.form.get('Current_city'),
                    "CURRENT_STATE": request.form.get('Current_state'),
                    "CURRENT_PINCODE": request.form.get('Current_pincode'),
                    "ADHAAR_NUMBER": request.form.get('Adhaar_Number'),
                    "PAN_NUMBER": request.form.get('pan_Number'),
                    "UPDATED_DATE": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

                }]

                stmt = db.met_emp_personal_details.update(). \
                    where(db.met_emp_personal_details.c.EMP_ID == bindparam('_EMP_ID')). \
                    values({"FIRST_NAME": bindparam('FIRST_NAME'), \
                            "LAST_NAME": bindparam('LAST_NAME'), \
                            # "ROLE": bindparam('ROLE'), \
                            # "EMAIL": bindparam('EMAIL'), \
                            "CONTACT_NO": bindparam('CONTACT_NO'), \
                            "CURRENT_ADDRESS": bindparam('CURRENT_ADDRESS'), \
                            "CURRENT_CITY": bindparam('CURRENT_CITY'), \
                            "CURRENT_STATE": bindparam('CURRENT_STATE'), \
                            "CURRENT_PINCODE": bindparam('CURRENT_PINCODE'), \
                            "PAN_NUMBER": bindparam('PAN_NUMBER'), \
                            "ADHAAR_NUMBER": bindparam('ADHAAR_NUMBER'), \
                            "UPDATED_DATE": bindparam('UPDATED_DATE'), \
                            })

                db.conn.execute(stmt, update_data)


            else:

                r = db.conn.execute(db.met_emp_personal_details.insert(),
                            EMP_ID=request.form.get('emp_id'),
                            FIRST_NAME=request.form.get('first_name'),
                            LAST_NAME=request.form.get('last_name'),
                            ROLE=request.form.get('role'),
                            EMAIL=request.form.get('email'),
                            CONTACT_NO=request.form.get('contact_no'),
                            CURRENT_ADDRESS=request.form.get('Current_address'),
                            CURRENT_CITY=request.form.get('Current_city'),
                            CURRENT_STATE=request.form.get('Current_state'),
                            CURRENT_PINCODE=request.form.get('Current_pincode'),
                            ADHAAR_NUMBER=request.form.get('Adhaar_Number'),
                            PAN_NUMBER=request.form.get('pan_Number'),
                            CREATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            UPDATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            )

            return redirect(url_for('index_bp.Employee_homePage'))
        return render_template("employee/add_personal_details.html",login_details=login_details,emp_personal_details=emp_personal_details
                               ,user_name=user_name,role=role
                               )
    else:
        print(False)
        return redirect(url_for('index_bp.index'))


@employee.route('/AttendancePage', methods=['POST', 'GET'])
@login_required
def attendance_page():
    print(session)


    if 'logged_in' in session:

        sql = "SELECT * FROM attendance_management WHERE EMP_ID ='{}' AND ROLE='{}'".format(
            session["USER_ID"], session["ROLE"])
        res = db.executeRawQueryAll(sql)
        attendance_management = db.fetchAllKeyValuePair(res)

        return render_template("employee/attendance_page1.html",attendance_management=attendance_management )
    else:
        print(False)
        return redirect(url_for('index_bp.index'))

@employee.route('/attendance_homepage', methods=['POST', 'GET'])
@login_required
def attendance_homepage():
    dictt1={}
    lis1=[]
    month_list=['01','02','03','04','05','06','07','08','09','10','11','12']

    for i in month_list:
        sql = "SELECT count(ID) AS count,DATE_FORMAT(DATE,'%M') AS MONTH,YEAR,(23-COUNT(ID)) AS ABSENT_DAYS  FROM attendance_management WHERE EMP_ID ='{}' AND ROLE='{}' AND MONTH='{}'".format(
            session["USER_ID"], session["ROLE"],i)
        res = db.executeRawQueryAll(sql)
        attendance_management = db.fetchAllKeyValuePair(res)
        if len(attendance_management)>0:
            lis1.append(attendance_management[0])

    print(lis1,'lis1')

    return render_template("employee/attendance_homepage.html",attendance_management=attendance_management,dictt1=lis1 )


def get_time_diffrence(selected_date):
    sql = "SELECT * FROM attendance_management WHERE EMP_ID ='{}' AND ROLE='{}' AND DATE='{}'".format(
        session["USER_ID"], session["ROLE"], request.form.get('selected_date'))
    res = db.executeRawQueryAll(sql)
    check_date1 = db.fetchAllKeyValuePair(res)
    if len(check_date1) > 0 :
        login_date_time1=datetime.datetime.strptime(check_date1[0]['LOGIN_TIME'],"%H:%M:%S")
        logout_date_time1=datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M:%S"),"%H:%M:%S")
    timedelta = logout_date_time1 - login_date_time1
    diffrence=round(timedelta.total_seconds()/3600,2)
    return diffrence

@employee.route('/AttendanceApi', methods=['POST', 'GET'])
@login_required

def attendance_api():

    print(request.form,'rrrrrrrrrrrr')
    day=request.form.get('selected_date')
    month_nd_year=request.form.get('selected_date').split('-')
    print(month_nd_year,'month_nd_year')

    sql = "SELECT * FROM attendance_management WHERE EMP_ID ='{}' AND ROLE='{}' AND DATE='{}'".format(
        session["USER_ID"], session["ROLE"], request.form.get('selected_date'))
    res = db.executeRawQueryAll(sql)
    check_date1 = db.fetchAllKeyValuePair(res)
    if len(check_date1) > 0 and request.form.get('data_type')=="Logout":
        diiffrences=get_time_diffrence(request.form.get('selected_date'))
        print(diiffrences,'*******')
    if 'logged_in' in session:

        if request.method=="POST" and request.form.get('data_type')=="Login":
            sql = "SELECT * FROM attendance_management WHERE EMP_ID ='{}' AND ROLE='{}' AND DATE='{}'".format(
                session["USER_ID"], session["ROLE"],request.form.get('selected_date'))
            res = db.executeRawQueryAll(sql)
            attendance_management = db.fetchAllKeyValuePair(res)
            if len(attendance_management)>0:
                return jsonify(code='200', status='success',msg='Details Already Stored!')

            else:

                r = db.conn.execute(db.met_attendance_management.insert(),
                                    ADMIN_ID=session['USER_ID'],
                                    EMP_ID=session['USER_ID'],
                                    FULL_NAME=session['FIRST_NAME']+" "+session['LAST_NAME'],
                                    ROLE=session['ROLE'],
                                    MONTH=month_nd_year[1],
                                    YEAR=month_nd_year[0],
                                    DATE=day,
                                    DATE_MONTH=month_nd_year[1] +' '+month_nd_year[0],
                                    CREATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    LOGIN_TIME=datetime.datetime.now().strftime("%H:%M:%S"),
                                    # LOGOUT_TIME=datetime.datetime.now().strftime("%H:%M:%S"),
                                    )

                return jsonify(code='200',status='success',msg='Your Attendance  has been Saved!')

        if request.method == "POST" and request.form.get('data_type') == "Logout":
            sql = "SELECT * FROM attendance_management WHERE EMP_ID ='{}' AND ROLE='{}' AND DATE='{}' AND LOGOUT_DATE IS NULL ".format(
                session["USER_ID"], session["ROLE"], request.form.get('selected_date'))
            print(sql,'logout uery')
            res = db.executeRawQueryAll(sql)
            attendance_management = db.fetchAllKeyValuePair(res)
            print(attendance_management,'attendance')
            if len(attendance_management) > 0:
                update_data = [{
                    "_EMP_ID":session["USER_ID"],
                    "LOGOUT_DATE": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "LOGOUT_TIME": datetime.datetime.now().strftime("%H:%M:%S"),
                }]
                stmt = db.met_attendance_management.update(). \
                    where(db.met_attendance_management.c.EMP_ID == bindparam('_EMP_ID')). \
                    values({
                            "LOGOUT_DATE": bindparam('LOGOUT_DATE'),
                            "LOGOUT_TIME": bindparam('LOGOUT_TIME'),
                            })
                db.conn.execute(stmt, update_data)
                return jsonify(code='200', status='success', msg='You are Successfully Logged out!')


            else:
                return jsonify(code='200', status='success', msg='Invalid Request')



    else:
        print(False)
        return jsonify(code='201',status='failed',msg='Failed')

@employee.route('/Leaves_Dashboard', methods=['POST', 'GET'])
@login_required
def leaves_dashboard():
    sql = "SELECT *  FROM leaves_application WHERE EMP_ID ='{}' AND ROLE='{}' ".format(
        session["USER_ID"], session["ROLE"],)
    res = db.executeRawQueryAll(sql)
    leaves_application = db.fetchAllKeyValuePair(res)
    print(leaves_application,'leaves_application')
    return render_template("employee/leaves_dashboard.html",leaves_application=leaves_application)


@employee.route('/Apply_Leave', methods=['POST', 'GET'])
@login_required
def Apply_Leave():
    sql = "SELECT *  FROM leaves_application WHERE EMP_ID ='{}' AND ROLE='{}' ".format(
        session["USER_ID"], session["ROLE"],)
    res = db.executeRawQueryAll(sql)
    leaves_application = db.fetchAllKeyValuePair(res)
    print(leaves_application,'leaves_application')
    dates_list=[]
    if request.method == "POST":
        dates_list=request.form.get('applied_dates').split(',')
        r = db.conn.execute(db.met_leaves_application.insert(),
                            EMP_ID=session['USER_ID'],
                            ROLE=session['ROLE'],
                            APPLIED_DATE=request.form.get('applied_dates'),
                            APPLIED_DAYS=len(dates_list),
                            REASON=request.form.get('reason'),
                            APPLIED_ON=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            )

        return redirect(url_for('employee.leaves_dashboard'))

    return render_template("employee/apply_leave.html")


@employee.route('/SalaryDashboard', methods=['POST', 'GET'])
@login_required
def salary_dashboard():
    sql = "SELECT *,DATE_FORMAT(CREATED_DATE,'%M - %Y') AS MONTH_YEAR  FROM salary_statement WHERE EMP_ID ='{}' AND ROLE='{}' ".format(
        session["USER_ID"], session["ROLE"],)
    res = db.executeRawQueryAll(sql)
    salary_statement = db.fetchAllKeyValuePair(res)
    return render_template("employee/salary_dashboard.html",salary_statement=salary_statement)
