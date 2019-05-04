from urllib.parse import urlparse, urljoin, unquote
import requests

import lxml.html
import sqlite3

import pathlib
import aiofiles
import asyncio

links = ["https://www.paavam.com/a-day-in-paris/",
         "http://voorburg2017-delhi.gov.in/index.php?option=com_content&view=article&id=17&Itemid=163"]
pdf_links = []

domains = [urlparse(url).netloc for url in links]

here = pathlib.Path(__file__).parent
outpath = here.joinpath("govt_db.db")
conn = sqlite3.connect(str(outpath))
c = conn.cursor()

for i in range(len(domains)):
    if ("-" in domains[i]):
        domains[i] = str(domains[i]).replace('-', '_')

# Create table
for domain in domains:
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

    def extractLinks(content):
        dom = lxml.html.fromstring(content)
        for link in dom.xpath('//a/@href'):
            # convert '/gallery' to full link "https://../gallery"
            if (urlparse(link).scheme != urlparse(new_url).scheme):
                link = urljoin(new_url, link)

            for file_type in ['.pdf', '.PDF']:
                if (file_type in link and link not in pdf_links):
                    if (requests.get(link).status_code != 404):
                        pdf_links.append(link)

                        domi = urlparse(link).netloc
                        if ("-" in domi):
                            domi = domi.replace('-', '_')

                        # Insert a row of data and commit
                        c.execute(
                            """INSERT INTO {domain} (urls, file_name, source_url) VALUES (?,?,?)""".format(
                                domain=domi.replace('.', '_')), (link, unquote(link).split("/")[-1], new_url))
                        conn.commit()

    extractLinks(content)


for new_url in links:
    scrapeIt(new_url)

print("Fetching files complete!")


def checkForUpdates(new_url):
    here = pathlib.Path(__file__).parent
    outpath = here.joinpath("govt_db.db")
    conn = sqlite3.connect(str(outpath))
    c = conn.cursor()

    domi = urlparse(new_url).netloc

    if ("-" in domi):
        domi = domi.replace('-', '_')

    c.execute("SELECT * FROM '{url}';".format(
        url=domi.replace(".", "_")))

    data = c.fetchall()
    file_details = []

    for i in range(len(data)):
        file_detail = {
            'db_file_name': data[i][1],
            # 'db_department': data[i][3],
            'db_site_pdf_url': data[i][0],
            'db_pdf_download_link': data[i][0],
        }

        file_details.append(file_detail)

    print(file_details)


checkForUpdates("https://www.paavam.com")
