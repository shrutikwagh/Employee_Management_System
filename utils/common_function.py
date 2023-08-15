from cryptography.fernet import Fernet
from utils import db
from utils.db import *
from flask import session
import smtplib



def generate_key():
    # generate_key1=Fernet.generate_key()
    # generate_key=Fernet(generate_key1)
    # print(generate_key)

    return open("secret.key", "rb").read()


def encrypt_psw(psw):

    key=generate_key()
    encoded_message = str(psw).encode()
    print(encoded_message,'encoded_message')
    f=Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message

def decrypt_msg(encrypted_message):
    print(encrypted_message,'encrypted message in decrypt function')
    key=generate_key()
    f=Fernet(key)
    decrypted_message1 = f.decrypt(encrypted_message)
    decrypted_message = decrypted_message1.decode('utf-8')
    print(decrypted_message,'decrypted_message')

    return decrypted_message



def module_access(email,password):
    print(email,password,'email,password')
    sql="SELECT * FROM login_details WHERE EMP_ID ='{}'".format(email)
    res=db.executeRawQueryAll(sql)
    login_details=db.fetchAllKeyValuePair(res)
    if len(login_details)>0:
        print('Login Successfull')
        password1=decrypt_msg(login_details[0]['PASSWORD'])
        print(login_details[0]['PASSWORD'],"login_details[0]['PASSWORD']")
        print(password1,'password1',type(password1),str(password1))
    if len(login_details)>0 and  password==password1:

        print('both the conditions are satisfied')
        session['EMAIL'] = login_details[0]['EMAIL']
        session['ROLE'] = login_details[0]['ROLE']
        session['FIRST_NAME'] = login_details[0]['FIRST_NAME']
        session['LAST_NAME'] = login_details[0]['LAST_NAME']
        session['ROLE'] = login_details[0]['ROLE']
        session['logged_in'] = True
        session['message'] = "You are Logged IN"
        role=login_details[0]['ROLE']
        if role!='' and role!='Admin':
            session['USER_ID']=login_details[0]['EMP_ID']

        elif role=="Admin":
            session['USER_ID'] = login_details[0]['EMP_ID']

        if role=="Admin":

            return redirect(url_for("index_bp.Admin_homepage"))

        else:
            return redirect('\Employee_homePage')


    else:
        session.pop('EMAIL', None)
        session.pop('USER_ID', None)
        session.pop('ROLE', None)
        session.pop('FIRST_NAME', None)
        session.pop('LAST_NAME', None)
        session.pop('logged_in', None)
        session['message'] = "You are Logged Out"
        return redirect('\index')


