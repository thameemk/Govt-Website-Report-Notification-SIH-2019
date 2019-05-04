from urllib.parse import urlparse, urljoin, unquote
import requests

import lxml.html
import sqlite3

import pathlib
import aiofiles
import asyncio
from . import mail_sender

links = []
pdf_links = []


def beginWork(new_url):
    if (new_url):
        links.append(new_url)
    else:
        return

    domain = urlparse(new_url).netloc

    here = pathlib.Path(__file__).parent
    outpath = here.joinpath("govt_db.db")
    conn = sqlite3.connect(str(outpath))
    c = conn.cursor()

    if ("-" in domain):
        domain = str(domain).replace('-', '_')

    # Create table
    try:
        c.execute("CREATE TABLE {url} (urls TEXT PRIMARY KEY, file_name TEXT, source_url TEXT);".format(
            url=domain.replace('.', '_')))
    except sqlite3.Error as e:
        c.execute("DROP TABLE {url};".format(url=domain.replace('.', '_')))
        c.execute("CREATE TABLE {url} (urls TEXT PRIMARY KEY, file_name TEXT, source_url TEXT);".format(
            url=domain.replace('.', '_')))
        print('[-] Sqlite operational error: {} Retrying...'.format(e))

    def scrapeIt(new_url):
        content = requests.get(new_url).content
        domain = urlparse(new_url).netloc

        if ("-" in domain):
            domain = domain.replace('-', '_')

        def extractLinks(content):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):
                if (urlparse(link).netloc == domain):
                    # convert '/gallery' to full link "https://../gallery"
                    if (urlparse(link).scheme != urlparse(new_url).scheme):
                        link = urljoin(new_url, link)

                        if ('.pdf' in link.lower() and link not in pdf_links):
                            print("2: " + link)
                            if (requests.get(link).status_code != 404):
                                print("3: " + link)
                                pdf_links.append(link)
                                c.execute("INSERT INTO " + domain.replace('.',
                                                                          '_') + " (urls, file_name, source_url) VALUES (?,?,?)",
                                          (link, unquote(link).split("/")[-1], new_url))
                                print("blahhhed: " + link)

                                # # Insert a row of data and commit
                                # c.execute(
                                #     """INSERT INTO {domain} (urls, file_name, source_url) VALUES (?,?,?)""".format(
                                #         domain=domi.replace('.', '_')), (link, unquote(link).split("/")[-1], new_url))

            conn.commit()

        extractLinks(content)

    print("Processing... %s" % (new_url))
    scrapeIt(new_url)
    print(pdf_links)

    print("Fetching files complete!")


def checkForUpdates(new_url):
    here = pathlib.Path(__file__).parent
    outpath = here.joinpath("govt_db.db")
    conn = sqlite3.connect(str(outpath))
    c = conn.cursor()

    domi = urlparse(new_url).netloc
    print("domain:  " + domi)

    if ("-" in domi):
        domi = domi.replace('-', '_')

    c.execute("SELECT * FROM '{url}';".format(
        url=domi.replace(".", "_")))

    datas = c.fetchall()
    # print(datas)

    pdf_links = []

    for data in datas:
        pdf_links.append(data[0])

    # print('Thisssss')
    print(pdf_links)

    prev_len = len(pdf_links)
    print("New URL IS : " + new_url)
    beginWork(new_url)

    print("New length: %d" % (len(pdf_links)))
    print("Previous length: %d" % (prev_len))

    if (len(pdf_links) != prev_len):
        print("something updated!")
        print(pdf_links[-1])
        mail_sender.sendMailMultiple(
            pdf_links[-1], pdf_links.split("/")[-1])
        c.execute("insert into '{url} (urls, file_name, souce_url) values(?,?,?)';".format(
            url=domi.replace(".", "_")), (pdf_links[-1], pdf_links.split("/")[-1]), new_url)

        print("Yassss!")
