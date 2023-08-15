import datetime
import gc

from flask import (Blueprint, render_template, redirect, request, jsonify, url_for, flash)

from utils.db import *
from utils.common_function import *
from flask import session
from os.path import join, dirname, realpath,os
from views.email_sending import  *

index_bp = Blueprint("index_bp", __name__)





@index_bp.route('/index', methods=['POST', 'GET'])

def index():

    print(session)
    if request.method=="POST":
        print(True)
        print(request.form)

        if request.form.get('email') and  request.form.get('password'):
            email=request.form.get('email')
            password=request.form.get('password')
            return module_access(email=email,password=password)

    return render_template("resgister.html")

@index_bp.route('/test', methods=['POST', 'GET'])
def test():
    return render_template("test.html")




@index_bp.route('/homepage', methods=['POST', 'GET'])
@login_required
def homepage():
    print(session)

    user_name=login_details=''
    if 'logged_in' in session:
        print(True)
        role = session['ROLE']
        user_id = session['USER_ID']
        sql = "SELECT * FROM login_details WHERE ROLE !='Admin'".format(user_id, role)
        print(sql)
        res = db.executeRawQueryAll(sql)
        login_details = db.fetchAllKeyValuePair(res)
        # if len(login_details)>0:
        user_name=session['FIRST_NAME']+' '+session['LAST_NAME']

        return render_template("homepage.html",user_name=user_name,login_details=login_details,role=role)
    else:
        user_name=''
        print(False)

        return redirect(url_for('index_bp.index'))


@index_bp.route('/Employee_homePage', methods=['POST', 'GET'])
@login_required
def Employee_homePage():
    print(session)
    user_name=login_details=''
    if 'logged_in' in session:
        role = session['ROLE']
        user_id = session['USER_ID']
        sql = "SELECT * FROM login_details WHERE EMP_ID ='{}' AND ROLE='{}'".format(user_id, role)
        res = db.executeRawQueryAll(sql)
        login_details = db.fetchAllKeyValuePair(res)
        user_name=session['FIRST_NAME']+' '+session['LAST_NAME']

        sql = "SELECT * FROM emp_personal_details WHERE EMP_ID ='{}' AND ROLE='{}'".format(user_id, role)
        print(sql,'sqlll')
        res = db.executeRawQueryAll(sql)
        emp_personal_details = db.fetchAllKeyValuePair(res)
        if len(emp_personal_details)>0:
            emp_personal_details1=emp_personal_details[0]
        else:
            emp_personal_details1={}
        return render_template("homepage1.html",user_name=user_name,login_details=login_details,emp_personal_details1=emp_personal_details1,role=role)
    else:
        user_name=''
        return redirect(url_for('index_bp.index'))




@index_bp.route('/AddEmployee', methods=['POST', 'GET'])
@login_required
def add_employee():
    print(session)

    if 'logged_in' in session:
        response = {}

        emp_id = genSequenceId('EMP')
        if request.method=="POST":

            psw = request.form.get('Password')
            emp_id1=request.form.get('emp_id')
            encrypt_psw1 = encrypt_psw(psw)
            decrypt_msg1 = decrypt_msg(encrypt_psw1)
            print(encrypt_psw1, 'enncrypted_psw')
            print(decrypt_msg1, 'decrypt_msg1')

            receiver_email = request.form.get('email')
            role = request.form.get('role')
            joining_date = request.form.get('Joining_Date')
            Salary = request.form.get('Salary')
            emp_name = request.form.get('first_name') + " "+request.form.get('last_name')
            Annual_ctc=int(Salary)*12

            generate_offer_letter1 = generate_offer_letter(emp_id1,emp_name,role,joining_date,Salary,receiver_email,psw)
            print(generate_offer_letter1, 'generate_offer_letter1')

            if generate_offer_letter1.get('status')=="success":

                r1 = save_doc_data(generate_offer_letter1.get('data'))
                response['status'] = generate_offer_letter1.get('status')
                response['message'] = generate_offer_letter1.get('message')
                print(response, '---response for pan_doc------')

            else:
                response['status'] = 'failed'
                response['message'] = 'File is not Attached'
                print(response, '---response for pan_doc------')

            r = db.conn.execute(db.met_login_details.insert(),
                        ADMIN_ID=session['USER_ID'],
                        EMP_ID=request.form.get('emp_id'),
                        FIRST_NAME=request.form.get('first_name'),
                        LAST_NAME=request.form.get('last_name'),
                        ROLE=request.form.get('role'),
                        PASSWORD=encrypt_psw1,
                        EMAIL=request.form.get('email'),
                        CREATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        UPDATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
            r = db.conn.execute(db.met_emp_personal_details.insert(),
                        ADMIN_ID=session['USER_ID'],
                        EMP_ID=request.form.get('emp_id'),
                        FIRST_NAME=request.form.get('first_name'),
                        LAST_NAME=request.form.get('last_name'),
                        ROLE=request.form.get('role'),
                        EMAIL=request.form.get('email'),
                        JOINING_DATE=request.form.get('joining_date'),
                        ANNUAL_CTC=Annual_ctc,
                        SALARY_MONTHLY=request.form.get('Salary'),
                        CREATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        UPDATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )

            return redirect(url_for('index_bp.Admin_homepage'))

        return render_template("add_employee.html",emp_id=emp_id)
    else:
        print(False)

        return render_template("resgister.html")



@index_bp.route('/AddAdmin', methods=['POST', 'GET'])
@login_required
def add_admin():
    psw=request.form.get('Password')
    encrypt_psw1=encrypt_psw(psw)
    decrypt_msg1=decrypt_msg(encrypt_psw1)
    print(encrypt_psw1,'enncrypted_psw')
    print(decrypt_msg1,'decrypt_msg1')

    # if 'logged_in' in session:
    emp_id=genSequenceId('AD')
    if request.method=="POST":

        r = db.conn.execute(db.met_login_details.insert(),
                    ADMIN_ID=emp_id,
                    EMP_ID=request.form.get('emp_id'),
                    FIRST_NAME=request.form.get('first_name'),
                    LAST_NAME=request.form.get('last_name'),
                    ROLE="Admin",
                    PASSWORD=encrypt_psw1,
                    EMAIL=request.form.get('email'),
                    CREATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    UPDATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )

        return redirect(url_for('index_bp.Admin_homepage'))
    #     return render_template("add_employee.html",emp_id=emp_id)
    # else:
    #     print(False)
    #
    return render_template("add_admin.html",emp_id=emp_id)









@index_bp.route("/logout")
@login_required
def logout():
    # session.clear()
    # gc.collect()
    try:

        session.pop('USER_ID', None)
        session.pop('logged_in', None)
    except Exception as e:
        print(e)
    return redirect(url_for('index_bp.index'))




@index_bp.route('/Admin_homepage', methods=['POST', 'GET'])
@login_required
def Admin_homepage():
    print(session)
    user_name=login_details=''

    role = session['ROLE']
    user_id = session['USER_ID']
    sql = "SELECT * FROM emp_personal_details WHERE ADMIN_ID ='{}' AND ROLE!='Admin'".format(user_id, role)
    print(sql)
    res = db.executeRawQueryAll(sql)
    emp_personal_details = db.fetchAllKeyValuePair(res)
    if len(emp_personal_details)>0:
        for row in emp_personal_details:
            row['url']=View_Docs(row['EMP_ID'],"offer_letter")

    user_name=session['FIRST_NAME']+' '+session['LAST_NAME']
    role=session['ROLE']

    return render_template("homepage_admin.html",user_name=user_name,login_details=emp_personal_details,role=role)


@index_bp.route('/View_offer_letter', methods=['POST', 'GET'])
@login_required
def view_offer_letter():
    print(session)
    user_name=login_details=''
    if 'logged_in' in session:
        print(True)
        role = session['ROLE']
        user_name=session['FIRST_NAME']+' '+session['LAST_NAME']
        user_id = session['USER_ID']

        return render_template("view_offer_letter.html",user_name=user_name,login_details=login_details,role=role)
    else:
        user_name=role=''
        print(False)

        return redirect(url_for('index_bp.index'))


@index_bp.route('/View_Employee_Details/<emp_id>', methods=['POST', 'GET'])
@login_required
def view_employee_details(emp_id):
    user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']

    sql = "SELECT * FROM emp_personal_details WHERE ADMIN_ID ='{}' AND EMP_ID!='Admin'".format(session['USER_ID'], emp_id)
    print(sql)
    res = db.executeRawQueryAll(sql)
    emp_personal_details = db.fetchAllKeyValuePair(res)
    if len(emp_personal_details)>0:
        emp_personal_details1=emp_personal_details[0]


    return render_template("view_employee_details.html",role=session['ROLE'],user_name=user_name,emp_personal_details1=emp_personal_details1)

@index_bp.route('/View_Leave_Applications', methods=['POST', 'GET'])
@login_required
def view_leave_applications():
    user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']

    sql = "SELECT * FROM leaves_application "
    res = db.executeRawQueryAll(sql)
    leaves_application = db.fetchAllKeyValuePair(res)

    return render_template("view_leave_applications.html",role=session['ROLE'],user_name=user_name,
                           leaves_application=leaves_application)


@index_bp.route('/Salary_Dashboard_Admin/<emp_id>', methods=['POST', 'GET'])
@login_required
def salary_dashboard_admin(emp_id):
    user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']

    sql = "SELECT * FROM salary_statement "
    res = db.executeRawQueryAll(sql)
    salary_statement = db.fetchAllKeyValuePair(res)

    return render_template("salary_dashboard_admin.html",role=session['ROLE'],user_name=user_name,
                           salary_statement=salary_statement,emp_id=emp_id)


@index_bp.route('/Generate_Salary_slip/<emp_id>', methods=['POST', 'GET'])
@login_required
def generate_salary_slip(emp_id):
    user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']

    sql = "SELECT * FROM emp_personal_details WHERE EMP_ID='{}' ".format(emp_id)
    res = db.executeRawQueryAll(sql)
    emp_personal_details = db.fetchAllKeyValuePair(res)
    if len(emp_personal_details)>0:
        emp_personal_details1=emp_personal_details[0]
    else:
        emp_personal_details1={}

    sql = "SELECT * FROM salary_statement "
    res = db.executeRawQueryAll(sql)
    salary_statement = db.fetchAllKeyValuePair(res)
    month_list=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    return render_template("Generate_Salary_slip.html",role=session['ROLE'],user_name=user_name,
                           salary_statement=salary_statement,emp_id=emp_id,month_list=month_list,emp_personal_details1=emp_personal_details1)




@index_bp.route('/Salary_slip_template/<emp_id>', methods=['POST', 'GET'])
@login_required
def Salary_slip_template(emp_id):
    user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']

    sql = "SELECT * FROM emp_personal_details WHERE EMP_ID='{}' ".format(emp_id)
    res = db.executeRawQueryAll(sql)
    emp_personal_details = db.fetchAllKeyValuePair(res)
    if len(emp_personal_details)>0:
        emp_personal_details1=emp_personal_details[0]
    else:
        emp_personal_details1={}

    sql = "SELECT * FROM salary_statement "
    res = db.executeRawQueryAll(sql)
    salary_statement = db.fetchAllKeyValuePair(res)
    month_list=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    return render_template("salary_slip_template.html",role=session['ROLE'],user_name=user_name,
                           salary_statement=salary_statement,emp_id=emp_id,month_list=month_list,emp_personal_details1=emp_personal_details1)





@index_bp.route('/Update_Leave_Applications/<emp_id>/<id>', methods=['POST', 'GET'])
@login_required
def update_leave_applications(emp_id,id):
    user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']

    sql = "SELECT * FROM leaves_application  WHERE EMP_ID='{}' AND ID='{}'".format(emp_id,id)
    res = db.executeRawQueryAll(sql)
    leaves_application = db.fetchAllKeyValuePair(res)
    if len(leaves_application)>0:
        leaves_application1=leaves_application[0]

    if request.method=="POST":


        update_data = [{
            "_ID":id,
            "STATUS":request.form.get('Status'),
            "APPROVED_ON": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "APPROVED_BY": session['FIRST_NAME']+' '+session['LAST_NAME'],
            "ADMIN_ID": session['USER_ID'],
        }]
        stmt = db.met_leaves_application.update(). \
            where(db.met_leaves_application.c.ID == bindparam('_ID')). \
            values({
            "STATUS": bindparam('STATUS'),
            "APPROVED_ON": bindparam('APPROVED_ON'),
            "APPROVED_BY": bindparam('APPROVED_BY'),
            "ADMIN_ID": bindparam('ADMIN_ID'),
        })
        db.conn.execute(stmt, update_data)
        return redirect(url_for('employee.View_Leave_Applications'))

    return render_template("update_leave_applications.html",role=session['ROLE'],user_name=user_name,
                           leaves_application=leaves_application1,emp_id=emp_id)




@index_bp.route('/Generate_Salary_Slip_Api', methods=['POST', 'GET'])
@login_required
def Generate_Salary_Slip_Api():
    print(request.form,'reqqqqqqqqq')
    current_year=datetime.datetime.now().strftime("%Y")
    month_name=request.form.get('month_name')
    emp_id=request.form.get('emp_id')
    # user_name = session['FIRST_NAME'] + ' ' + session['LAST_NAME']
    #

    if request.method=="POST":
        sql = "SELECT * FROM salary_statement  WHERE EMP_ID='{}' AND MONTH='{}' AND YEAR='{}'".format(emp_id,month_name,current_year)
        res = db.executeRawQueryAll(sql)
        salary_statement = db.fetchAllKeyValuePair(res)
        if len(salary_statement)>0:
            salary_statement1=salary_statement[0]
            update_data = [{
                "_ID":id,
                "STATUS":request.form.get('Status'),
                "APPROVED_ON": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "APPROVED_BY": session['FIRST_NAME']+' '+session['LAST_NAME'],
                "ADMIN_ID": session['USER_ID'],
            }]
            stmt = db.met_leaves_application.update(). \
                where(db.met_leaves_application.c.ID == bindparam('_ID')). \
                values({
                "STATUS": bindparam('STATUS'),
                "APPROVED_ON": bindparam('APPROVED_ON'),
                "APPROVED_BY": bindparam('APPROVED_BY'),
                "ADMIN_ID": bindparam('ADMIN_ID'),
            })
            db.conn.execute(stmt, update_data)


        else:

            r = db.conn.execute(db.met_salary_statement.insert(),
                        ADMIN_ID=session['USER_ID'],
                        EMP_ID=request.form.get('emp_id'),
                        SALARY=request.form.get('salary'),
                        MONTH=request.form.get('month_name'),
                        YEAR=current_year,
                        ROLE=request.form.get('role'),
                        CREATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        UPDATED_DATE=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )

    return jsonify(code=200,status="success")








def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print('decorator called')
        if 'logged_in' in session and session['logged_in']:
            print('cccccccccccc')
            return f(*args, **kwargs)
        else:
            return redirect('/index')

    return wrap

