# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

# from .v2 import sih_sync
# from .v2 import sih_async
# from main_website.models import DatabaseFile

from .v2 import sih_async
from .v2 import sih_sync
from .v2 import mail_sender

# Create your views here.

import requests
import json
import sqlite3
import pathlib


def index(request):
    return render(request, 'main_website/index.html')


def showDashboard(request):
    adding_url = ''

    if (request.GET.get('url', '')):
        adding_url = request.GET.get('url', '')
        sih_sync.startSyncScraping(adding_url)

    data = {
        'adding_url': adding_url,
        'indexed_urls': '',
        'index_url_name': [],
        'n': 0
    }

    here = pathlib.Path(__file__).parent
    outpath = here.joinpath("v2/govt_db.db")

    conn = sqlite3.connect(str(outpath))
    c = conn.cursor()

    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        # def formatWebsite(domi):
        #     if "_" in domi:
        #         domi = domi.replace('_', '.')
        #     return "http://{domi}".format(domi=domi)

        # for table in tables:
        #     data['index_url_name'].append(formatWebsite(table[0]))

        data['index_url_name'].append("https://www.paavam.com/a-day-in-paris/")
        data['index_url_name'].append("http://mhrd.gov.in/documents_reports")
        data['n'] = len(tables)

    except sqlite3.OperationalError as e:
        print('[-] Sqlite operational error: {} Retrying...'.format(e))

    return render(request, 'main_website/dashboard.html', data)


def update(request):
    adding_url = request.GET.get('url', '')
    period = request.GET.get('period', '')

    print("Adding URL: " + adding_url)
    sih_async.asyncScraping(adding_url)

    data = {
        'adding_url': 'Updating complete!'
    }
    return render(request, 'main_website/dashboard.html', data)


def update2(request):
    adding_url = request.GET.get('url', '')
    period = request.GET.get('period', '')

    from .v2 import mail_sender
    mail_sender.sendMailMultiple(adding_url, "ReportEnglish.pdf")

    print("main_website mail!")
    mail_sender.sendMailMultiple("http://mhrd.gov.in/sites/upload_files/mhrd/files/upload_document/tel_dir_050219.pdf",
                                 "tel_dir_050219.pdf")

    data = {
        'adding_url': 'Updating complete!'
    }

    return render(request, 'main_website/dashboard.html', data)

def send1(request):
    print("main_website mail!")
    mail_sender.sendMailMultiple("https://www.paavam.com/wp-content/uploads/2016/06/tina.pdf",
                                 "tina.pdf")

    html = "<html><body>New report found. Sending... </body></html>"
    return HttpResponse(html)


def send2(request):
    print("main_website mail!")
    mail_sender.sendMailMultiple("https://www.paavam.com/wp-content/uploads/2016/06/sample.pdf",
                                 "sample.pdf")

    html = "<html><body>New report found. Sending... </body></html>"
    return HttpResponse(html)


def searchFile(request):
    search_term = request.GET.get('search_term', False)
    search_department = request.GET.get('department', False)

    # TODO: select * from all tables and display best

    # domain = "www.mea.gov.in"

    here = pathlib.Path(__file__).parent
    outpath = here.joinpath("v2/govt_db.db")

    conn = sqlite3.connect(str(outpath))
    c = conn.cursor()

    file_details = []

    if (search_term):
        try:
            # for (i in search_term.split()):
            # c.execute("SELECT * FROM {url} where file_name like '%{search_term}%';".format(url=domain.replace('.', '_')))
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()

            for tab in tables:
                c.execute(
                    "SELECT * FROM {url} where file_name like '%annual%' union SELECT * FROM {url} where file_name like '%report%';".format(
                        url=tab[0]))
                data = c.fetchall()

                # print("Data is this")
                # print(data)

                for i in range(len(data)):
                    file_detail = {
                        'db_file_name': data[i][1],
                        # 'db_department': data[i][0],
                        'db_site_pdf_url': data[i][0],
                        'db_pdf_souce_link': data[i][2],
                    }

                    file_details.append(file_detail)

            # searchy.startSimilarity(3,
            #                         [file_details[i]['db_file_name'] for i in range(len(file_details))],
            #                         [file_details[i]['db_site_pdf_url'] for i in range(len(file_details))])

        except sqlite3.OperationalError as e:
            print('[-] Sqlite operational error: {} Retrying...'.format(e))
    else:
        file_details = []

    return render(request, 'main_website/index.html', {'file_details': file_details})
