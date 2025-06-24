from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect 
from django.contrib import admin, messages
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]