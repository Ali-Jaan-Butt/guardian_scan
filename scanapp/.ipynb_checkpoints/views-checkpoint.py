from django.shortcuts import render
import pymongo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import requests
import plotly.express as px
import plotly.io as pio
import pandas as pd
from django.http import HttpResponse
from django.template.loader import render_to_string
import pyautogui
from django.core.files.storage import default_storage
from PIL import Image
import os
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader

def myapp(request):
    obj = None
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    database_name = "Guardian_Scan"
    db = client[database_name]
    collection_name = "email"
    collection = db[collection_name]
    cursor = collection.find()
    for document in cursor:
        obj = document
    if obj != None:
        email = { '$set':{'Email':None}}
        collection.update_one(obj, email)
    else:
        collection.insert_one({'Email':None})
    return render(request,"temp/front.html")

def signup(request):
    return render(request, 'temp/signup.html')

def login(request):
    return render(request, 'temp/login.html')

def gard_scan(request):
    return render(request, 'temp/scanning.html')

def forget(request):
    return render(request, 'temp/email_verification.html')

def ver_code(request):
    return render(request, 'temp/verification_code.html')

def up_pass(request):
    return render(request, 'temp/update_password.html')

def contact(request):
    return render(request, 'temp/contact.html')

def signup_def(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        sign = {'Name':name, 'Email':email, 'Password':password}
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        database_name = "Guardian_Scan"
        db = client[database_name]
        collection_name = "signup"
        collection = db[collection_name]
        collection.insert_one(sign)
    return myapp(request)

def login_def(request):
    if request.method == 'POST':
        con_email = None
        con_pass = None
        email = request.POST.get('email')
        password = request.POST.get('password')
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        database_name = "Guardian_Scan"
        db = client[database_name]
        collection_name = "signup"
        collection = db[collection_name]
        cursor = collection.find()
        for document in cursor:
            obj = document
            if email==obj['Email'] and password==obj['Password']:
                con_email = email
                con_pass = password
                pass
            else:
                msg_alert = 'Invalid Email or Password'
        if con_email != None:
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            database_name = "Guardian_Scan"
            db = client[database_name]
            collection_name = "login"
            collection = db[collection_name]
            log = {'Email':con_email, 'Password':con_pass}
            collection.insert_one(log)
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            database_name = "Guardian_Scan"
            db = client[database_name]
            collection_name = "email"
            collection = db[collection_name]
            cursor = collection.find()
            for document in cursor:
                obj = document
            up_email = { '$set':{'Email':con_email}}
            collection.update_one(obj, up_email)
            return gard_scan(request)
        else:
            return render(request, 'temp/login.html', {'msg_alert':msg_alert})
    return email

letters_and_digits = string.ascii_letters + string.digits
code = ''.join(random.choice(letters_and_digits) for i in range(6))

def forget_email(request):
    ver_email = None
    email = request.POST.get('email')
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    database_name = "Guardian_Scan"
    db = client[database_name]
    collection_name = "signup"
    collection = db[collection_name]
    cursor = collection.find()
    for document in cursor:
        obj = document
        if obj['Email'] == email:
            ver_email = email
            with open('up_email.txt', 'w') as file:
                file.write(ver_email)
        else:
            msg_alert = 'Invalid Email'
    if ver_email != None:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login('guardianscanpk@gmail.com', 'gqru lqys dgyd zqcf')
            subject = 'Verification Code'
            body = 'Your verification code is: '+str(code)
            msg = f'Subject: {subject}\n\n{body}'
            smtp.sendmail('guardianscanpk@gmail.com', ver_email, msg)
        return ver_code(request)
    else:
        return render(request, 'temp/email_verification.html', {'msg_alert':msg_alert})
    return email

def code_verify(request):
    if request.method == 'POST':
        in_code = request.POST.get('code')
        if in_code == code:
            return up_pass(request)
        else:
            msg_alert = 'Invalid code'
            return render(request, 'temp/verification_code.html', {'msg_alert':msg_alert})
    return in_code

def conf_pass(request):
    if request.method == 'POST':
        password = request.POST.get('passw')
        conf_password = request.POST.get('con_pass')
        if password == conf_password:
            eq_pass = password
            with open('up_email.txt', 'r') as file:
                up_email = file.read()
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            database_name = "Guardian_Scan"
            db = client[database_name]
            collection_name = "signup"
            collection = db[collection_name]
            cursor = collection.find()
            for document in cursor:
                obj = document
                if obj['Email'] == up_email:
                    set_name = obj['Name']
                    set_email = obj['Email']
                    pass
                else:
                    pass
            upd_email = { '$set':{'Name':set_name, 'Email':set_email, 'Password':eq_pass}}
            collection.update_one(obj, upd_email)
            return login(request)
        else:
            msg_alert = 'Password and Confirm Password are not same'
            return render(request, 'temp/update_password.html', {'msg_alert':msg_alert})
    return password

def scan_web(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        type = request.POST.get('type')
        response = requests.get(url)
        headers = response.headers
        security_headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Referrer-Policy',
            'Permissions-Policy',
            'Strict-Transport-Security'
        ]
        missing_headers = [h for h in security_headers if h not in headers]
        if missing_headers:
            print(f"Missing security headers on {url}: {missing_headers}")
            values = []
            for v in range(len(missing_headers)):
                values.append(1)
            data = {
                'Missing Configurations': missing_headers,
                'Presence': values
            }
            fig = px.bar(data, x='Missing Configurations', y='Presence', title='Security Headers Report')
            chart_html = pio.to_html(fig, full_html=False)
            fig.write_image("scanapp/static/figures/figure.png", format='png')
            screenshot = pyautogui.screenshot()
            screenshot.save('static/figure.png')
        else:
            print(f"All recommended security headers are present on {url}.")
        # Second Module
        access = None
        user_data = None
        user_access = []
        admin_resource = 'admin_panel'
        user_session = requests.Session()
        user_session.auth = ('regular_user', 'password')
        response = user_session.get(f"{url}/{admin_resource}")
        if response.status_code == 200:
            access = "Security Flaw: Regular user can access admin resource!"
        else:
            access = "Access appropriately restricted."
        other_user_resource = 'user/12345/data'
        response = user_session.get(f"{url}/{other_user_resource}")
        if response.status_code == 200:
            user_data = "Security Flaw: User can access another user's data!"
        else:
            user_data = "User data is properly isolated."
        secure_endpoints = ['profile', 'settings', 'dashboard']
        for endpoint in secure_endpoints:
            response = requests.get(f"{url}/{endpoint}")
            if response.status_code == 200:
                user_access.append(f"Security Flaw: Unauthenticated access to {endpoint}!")
            else:
                user_access.append(f"Access to {endpoint} is secured.")
        global context
        context = {
            'chart': chart_html,
            'access': access,
            'user_data': user_data,
            'user_access': user_access
            }
        return render(request, 'temp/security_chart.html', context)
    return gard_scan(request)

def html_to_pdf_view(request):
    def convert_image_to_pdf(image_path, pdf_path):
        pdf_width = 800
        image = Image.open(image_path)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        img_width, img_height = image.size
        aspect_ratio = img_height / img_width
        pdf_height = pdf_width * aspect_ratio
        c = canvas.Canvas(pdf_path, pagesize=(pdf_width, pdf_height))
        image_reader = ImageReader(image)
        c.drawImage(image_reader, 0, 0, width=pdf_width, height=pdf_height)
        c.save()
        print(f"Image {image_path} has been converted to PDF and saved as {pdf_path}")
    def add_text_to_existing_pdf(input_pdf_path, output_pdf_path, text, position):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(position[0], position[1], text)
        can.save()
        packet.seek(0)
        new_pdf = PyPDF2.PdfReader(packet)
        existing_pdf = PyPDF2.PdfReader(open(input_pdf_path, "rb"))
        output = PyPDF2.PdfWriter()
        for i in range(len(existing_pdf.pages)):
            page = existing_pdf.pages[i]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
        with open(output_pdf_path, "wb") as output_stream:
            output.write(output_stream)
    image_path = 'scanapp/static/figures/figure.png'
    pdf_path = 'output.pdf'
    convert_image_to_pdf(image_path, pdf_path)
    text = context['access'] + '\n' + context['user_data'] + '\n' + str(context['user_access'])
    position = (50, 500)
    add_text_to_existing_pdf(pdf_path, pdf_path, text, position)
    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(pdf_path)}'
    return response

def queries(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        query = {'Name':name, 'Email':email, 'Subject':subject, 'Message':message}
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        database_name = "Guardian_Scan"
        db = client[database_name]
        collection_name = "query"
        collection = db[collection_name]
        collection.insert_one(query)
    return gard_scan(request)