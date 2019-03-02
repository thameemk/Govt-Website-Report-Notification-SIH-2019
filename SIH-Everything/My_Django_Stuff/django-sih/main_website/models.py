# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Url(models.Model):
    url = models.TextField()
    file_name = models.TextField()

class DatabaseFile(models.Model):
    db_file_name = models.TextField()
    db_department = models.TextField()
    db_site_pdf_url = models.TextField()
    db_pdf_download_link = models.TextField()
