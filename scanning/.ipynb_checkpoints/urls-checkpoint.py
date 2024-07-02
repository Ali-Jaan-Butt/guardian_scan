"""
URL configuration for scanning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from scanapp import views
from scanapp.views import html_to_pdf_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.myapp, name="front"),
    path('sign-up', views.signup, name='signup'),
    path('log-in', views.login, name='login'),
    path('scan', views.gard_scan, name='scan'),
    path('update-password', views.up_pass, name='up-pass'),
    path('forget-pass', views.forget, name='forget'),
    path('change-pass', views.ver_code, name='code'),
    path('contact', views.contact, name='contact'),
    path('home', views.signup_def, name='sign-up-def'),
    path('guard-scan', views.login_def, name='log-in-def'),
    path('code', views.forget_email, name='ver_code'),
    path('up-pass', views.code_verify, name='update'),
    path('login', views.conf_pass, name='conf-pass'),
    path('scan-start', views.scan_web, name='scan-web'),
    path('download_pdf/', html_to_pdf_view, name='download_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)