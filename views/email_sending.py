import email, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from email.mime.multipart import MIMEMultipart
import pdfkit
from os.path import join, dirname, realpath,os

from utils import db
from utils.db import *
import boto3
from email import encoders
from utils.config import *
from flask import (Blueprint, render_template, redirect, request, jsonify, url_for, flash)
import  datetime
from sqlalchemy import bindparam,and_
# Gmail SMTP configuration

def send_email_test(receiver_email,emp_id,emp_name,role,password,doc_path,filename1):
    smtp_server = config.SMTP_SERVER
    smtp_port = 587
    sender_email =config.SMTP_MAIL # Replace with your Gmail email address
    sender_password = config.SMTP_PSW  # Replace with your Gmail password

    # receiver_email = 'itsshrutikawagh@gmail.com'
    # Replace with the recipient's email address
    subject = 'Welcome Onboard'
    body ="<p>Hi "+emp_name+",</p><br><br>"
    body +=" "
    body +="<p>Welcome to the team! We’re thrilled to have you at [company name] as a "+role+"."\
           " We know you’re going to be a valuable asset to our company and can’t wait to see what you accomplish.<br>"
    body +="Just a reminder, your first day is August 6. All you need to bring is yourself and some ID for your I-9. <br>" \
           "Our dress code is casual, so wear something comfy! As I mentioned before, we offer flexible work hours anytime between 7 a.m. and 7 p.m.<br>" \
           " For your first day, though, please arrive by 9:30 a.m., and feel free to park in any unmarked spot in the parking lot.</p>"
    body +="<br><br>"
    body +="<b>Employee ID:"+emp_id+"</b><br>"
    body +="<b>Login ID:"+emp_id+"</b><br>"
    body +="<b>Password :"+password+"</b><br>"
    body +="<br>"
    body +="<p>Welcome Onboard!<br>"
    body +="Company Name</p>"

    print(body,'bodyyyyyyyy')

    message = MIMEMultipart("alternative")
    body = MIMEText(body, "html")
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    message.attach(body)
    filename = str(doc_path)

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename1}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)

    # try:
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # server.ehlo()  # Can be omitted
        server.starttls(context=context)
        # server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print('Email sent successfully!')

    return 1

#C:\Program Files\wkhtmltopdf
def generate_offer_letter(emp_id,emp_name,role,joining_date,Salary,receiver_email,psw):
    response={}
    try:

        format_joining_date = datetime.datetime.strptime(joining_date, "%Y-%m-%d").strftime(
            "%d-%m-%Y")

        config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        # storing string to pdf file
        emp_name1=emp_name.replace(" ",'_')
        doc_path = join(os.path.abspath(join(dirname("__file__"), 'reports')),emp_name1+"_"+emp_id+"_offer_letter.pdf")
        todays_date=datetime.datetime.now().strftime("%d-%m-%Y")
        annual_ctc=int(Salary)*12

        generated_doc=pdfkit.from_string(render_template("view_offer_letter.html",emp_name=emp_name,role=role,joining_date=format_joining_date,todays_date=todays_date,Salary=Salary,annual_ctc=annual_ctc), doc_path, configuration=config)
        file_name=emp_name+"_"+emp_id+"_offer_letter.pdf"
        upload_s3=upload_toO_s3(doc_path,"hrmsshrutika",role,file_name)
        if upload_s3.get('status')=="success":
            send_mail = send_email_test(receiver_email, emp_id, emp_name, role, psw,str(doc_path),file_name)

            req_data={}
            req_data['EMP_ID']=emp_id
            req_data['ADMIN_ID']=session['USER_ID']
            req_data['DOC_PATH']=str(doc_path)
            req_data['DOC_NAME']=file_name
            req_data['DOC_TYPE']="offer_letter"
            save_doc_datas=save_doc_data(req_data)

            if os.path.exists(doc_path):
                os.remove(doc_path)
                print('offer letter file deleted from local folder successfully')
            else:
                print("The file does not exist")

        response['status'] = "success"

        response['message'] = "File Data Saved"

    except Exception as e:

        print(e, 'exception in generate_offer_letter doc_data')
        response['status'] = "failed"
        response['message'] = "Error occured while saving file data"
    return response




def upload_toO_s3(target_dir, bucket_name, appFormId,file_name):
    print(target_dir, bucket_name, appFormId,file_name,'target_dir, bucket_name, appFormId)')

    response = {}
    try:
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=config.IAM_KEY,
            aws_secret_access_key=config.SECRET_KEY)

        bucket = s3_resource.Bucket(bucket_name)

        # doc_path = join(os.path.abspath(join(dirname("__file__"), 'reports')), appFormId)
        # print(doc_path,'doc_path')
        f_name = file_name
        f = open(target_dir, "rb")
        result = bucket.Object(f_name).put(Body=f.read())

        response['status'] = "success"
        response['message'] = "File Uploaded Successfully"
        return response
    except Exception as e:
        print(e, "upload_toO_s3")
        response['status'] = "failed"
        response['message'] = "Error occured while uploading file"

    return response


def save_doc_data(req_data):
    print(req_data,'save_doc_data-------------')
    response = {}
    try:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        document_id = "DD" + current_date
        print(document_id, 'document_id')

        sql = "SELECT * FROM DOC_VAULT WHERE EMP_ID='{0}' and  DOC_TYPE='{1}'".format(
            req_data.get("EMP_ID"), req_data.get("DOC_TYPE"))
        res = db.executeRawQueryAll(sql)
        data_result = db.fetchAllKeyValuePair(res)
        if len(data_result) > 0:
            update_data = [{
                'EMP_ID': req_data.get('EMP_ID'),
                'DOC_ID': document_id,
                'ADMIN_ID': req_data.get('ADMIN_ID'),
                'DOC_NAME': req_data.get('DOC_NAME'),
                'DOC_PATH': req_data.get('DOC_PATH'),
                'DOC_TYPE': req_data.get('DOC_TYPE'),
                'UPDATED_DATE': current_date,
            }]
            stmt = db.met_doc_vault.update(). \
                where(and_(db.met_doc_vault.c.EMP_ID == bindparam('EMP_ID'),
                           db.met_doc_vault.c.DOC_TYPE == bindparam('DOC_TYPE')
                           )). \
                values({
                        "DOC_ID": bindparam('DOC_ID'), \
                        "ADMIN_ID": bindparam('ADMIN_ID'), \
                        "DOC_NAME": bindparam('DOC_NAME'), \
                        "DOC_PATH": bindparam('DOC_PATH'), \
                        "UPDATE_DATE": bindparam('UPDATE_DATE'), \
                        })
            db.conn.execute(stmt, update_data)
        else:
            r=db.conn.execute(db.met_doc_vault.insert(),
                            EMP_ID=req_data.get('EMP_ID'),
                            DOC_ID=document_id,
                            ADMIN_ID=req_data.get('ADMIN_ID'),
                            DOC_NAME=req_data.get('DOC_NAME'),
                            DOC_PATH=req_data.get('DOC_PATH'),
                            DOC_TYPE=req_data.get('DOC_TYPE'),
                            CREATED_DATE=current_date,
                            UPDATED_DATE=current_date,

                            )

        response['status'] = "success"
        response['message'] = "File Data Saved"

    except Exception as e:
        print(e,'exception in Save doc_data')
        response['status'] = "failed"
        response['message'] = "Error occured while saving file data"

    return response

def View_Docs(emp_id,doc_type):
    print("Function called")
    try:

        sql = "SELECT *  FROM " \
              "DOC_VAULT WHERE EMP_ID ='{}' AND DOC_TYPE='{}'".format(emp_id, doc_type)
        print(sql,'sqqqqqqqq')
        res = db.executeRawQueryAll(sql)
        bank_statement_1_result = db.fetchAllKeyValuePair(res)
        if len(bank_statement_1_result) > 0:
            output = url_of_file(bank_statement_1_result[0].get('DOC_NAME'))
            print(output,'yyyyyyyyyyyy')
            return output
        else:
            return "Document Not Found"
    except Exception as d:
        print(d, "dddddddddddddddddddddddddddddddddddddddddddddd")
        return "Document Not Found"


def url_of_file(doc_path):
    BUCKET_NAME = 'hrmsshrutika'  # replace with your bucket name
    KEY = "{0}".format(doc_path)
    print('KEYYYYYYYYYYYYYYYYYYYYYY',KEY,'KEYYYYYYYYYYYYYYYYYYYYYY')
    # replace with your object key
    ext = "pdf"
    if doc_path:
        try:
            ext = doc_path.split('.')[1]
        except Exception as e:
            print(e)

    if ext == 'doc':
        content_type = 'application/msword'
    elif ext == 'docx':
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif ext == 'csv':
        content_type = 'application/csv'
    elif ext == 'jpeg' or ext == 'jpg':
        content_type = 'image/jpeg,image/jpg'
    elif ext == 'png':
        content_type = 'image/png'
    else:
        content_type = 'application/pdf'
    try:

        sessions = boto3.session.Session(region_name='ap-south-1')
        s3_client = sessions.client('s3', config=boto3.session.Config(signature_version='s3v4'),
                                    aws_access_key_id=config.IAM_KEY,
                                    aws_secret_access_key=config.SECRET_KEY)
        return s3_client.generate_presigned_url(ClientMethod='get_object',
                                                Params={'Bucket': BUCKET_NAME, 'Key': KEY,
                                                        'ResponseContentType': content_type},
                                                ExpiresIn=600000, )

    except Exception as e:
        print(e)

    return "Document Not Found"

