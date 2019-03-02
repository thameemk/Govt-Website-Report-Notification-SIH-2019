# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from .v2 import sih_sync
from .v2 import sih_async
from main_website.models import DatabaseFile

# Create your views here.

import requests
import json
import sqlite3
import pathlib


def displayDatabase(url):
    print("hello")


def index(request):
    return render(request, 'main_website/index.html')


def showDashboard(request):
    adding_url = request.GET.get('url', '')

    if request.method == "GET" and len(adding_url):
        sih_sync.startSyncScraping(adding_url)
        sih_async.asyncScraping()
    else:
        print("No url provided!")

    data = {
        'adding_url': adding_url
    }

    return render(request, 'main_website/dashboard.html', data)


def searchFile(request):
    search_term = request.POST.get('search_term', False)
    department = request.POST.get('department', False)

    # TODO: select * from all tables and display best

    # datas = DatabaseFile()

    # db_file_name = request.GET['db_file_name']
    # db_department = request.GET['db_department']
    # db_site_pdf_url = fileParams.objects.get(id=db_site_pdf_url)
    # db_pdf_download_link = fileParams.objects.get(id=db_pdf_download_link)

    datas = {
        'db_file_name': 'db_file_name',
        'db_department': 'db_department',
        'db_site_pdf_url': 'db_site_pdf_url',
        'db_pdf_download_link': 'db_pdf_download_link',
        'n': range(2)
    }

    return render(request, 'main_website/index.html', datas)


# def addUrlDatabase(request):
#     if request.method == "GET":
#         scraping_url = request.GET['url']
#         sih_sync.startSyncScraping(scraping_url)
#     else:
#         print("No url provided!")
#
#     # sih_async.asyncScraping()
#     return render(request, 'main_website/dashboard.html')

# def say(request, say_this):
#     user = User.objects.get(id=say_this)
#
#     return render(request, 'main_website/about.html',)
