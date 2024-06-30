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

def myapp(request):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    database_name = "Guardian_Scan"
    db = client[database_name]
    collection_name = "email"
    collection = db[collection_name]
    cursor = collection.find()
    for document in cursor:
        obj = document
    email = { '$set':{'Email':None}}
    collection.update_one(obj, email)
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
        context = {
            'chart': chart_html,
            'access': access,
            'user_data': user_data,
            'user_access': user_access
            }
        return render(request, 'temp/security_chart.html', context)
    return gard_scan(request)

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from html.parser import HTMLParser

class HTMLToPDFParser(HTMLParser):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.y = 750  # Start height for text in PDF
        self.styles = {'h1': 24, 'h2': 18, 'p': 12}
        self.current_style = 'p'
        self.offset = 14

    def handle_starttag(self, tag, attrs):
        if tag in self.styles:
            self.current_style = tag

    def handle_endtag(self, tag):
        if tag in self.styles:
            self.y -= self.offset  # Add space after each element

    def handle_data(self, data):
        if self.current_style in self.styles:
            self.canvas.setFont("Helvetica", self.styles[self.current_style])
            self.canvas.drawString(72, self.y, data.strip())
            self.y -= self.styles[self.current_style] + 2  # Line height

def convert_html_to_pdf(html_content, response):
    c = canvas.Canvas(response, pagesize=letter)
    parser = HTMLToPDFParser(c)
    parser.feed(html_content)
    c.save()

def download_pdf(request):
    # with open('temp/security_chart.html', 'r', encoding='utf-8') as file:
    #     html_content = file.read()
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="security_headers_report.pdf"'
    res = requests.get('http://127.0.0.1:8000/scan-start')
    text = res.text
    convert_html_to_pdf(text, 'temp/report.pdf')
    return render(request, 'temp/security_chart.html')
