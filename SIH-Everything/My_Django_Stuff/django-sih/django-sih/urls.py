"""django-sih URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from main_website import views as v1

urlpatterns = [
    url(r'home', v1.index),
    url(r'^search/$', v1.searchFile, name='search'),
    url(r'^dashboard/$', v1.showDashboard, name='dashboard'),
    url(r'^add/$', v1.showDashboard, name='add'),
    url(r'^update/$', v1.update, name='update'),
    url(r'^api/send1$', v1.send1, name='update'),
    url(r'^api/send2$', v1.send1, name='update'),
    url(r'^update2/$', v1.update2, name='update2'),
]
