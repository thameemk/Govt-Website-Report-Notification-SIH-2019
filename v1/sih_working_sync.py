from urllib.parse import urlparse, urljoin, unquote
import requests

import lxml.html
import sqlite3

import pathlib

new_links = [];
visited_links = [];
pdf_links = []

not_url = ['/', '#', 'javascript:void(0)']
file_types = ['.pdf', '.doc', '.docx', '.xlxs', '.PDF']
not_file_types = ['.mp3', '.jpg', '.png', '.ppt', '.pptx', '.JPG']

# main_url = 'http://www.paavam.com'
url = 'http://mhrd.gov.in/'
domain = urlparse(url).netloc

here = pathlib.Path(__file__).parent
outpath = here.joinpath("govt_db.db")

conn = sqlite3.connect(str(outpath))
c = conn.cursor()

# Create table
try:
    c.execute("CREATE TABLE {url} (urls TEXT PRIMARY KEY, file_name TEXT);".format(
        url=domain.replace('.', '_')))
except sqlite3.OperationalError as e:
    c.execute("DROP TABLE {url};".format(url=domain.replace('.', '_')))
    c.execute("CREATE TABLE {url} (urls TEXT PRIMARY KEY, file_name TEXT);".format(
        url=domain.replace('.', '_')))
    print('[-] Sqlite operational error: {} Retrying...'.format(e))

def scrapeIt(new_url):
    content = requests.get(new_url).content

    def extractLinks(content):
        dom = lxml.html.fromstring(content)
        # print("" + new_url + " : " + str(len(dom.xpath('//a/@href'))))
        for link in dom.xpath('//a/@href'):
            # retun if '#' and links
            if (link not in not_url):
                # convert '/gallery' to full link "https://../gallery"
                if (urlparse(link).scheme != urlparse(new_url).scheme):
                    link = urljoin(new_url, link)

                # check for same domain links
                if (urlparse(link).netloc == domain):
                    # removing link parameters
                    if ('#' in link or '?' in link or '&' in link):
                        link = urljoin(url, urlparse(link).path)

                    for file_type in file_types:
                        if (file_type in link and link not in pdf_links):
                            if (requests.get(link).status_code != 404):
                                pdf_links.append(link)
                                # Insert a row of data and commit
                                # c.execute("INSERT INTO " + url + " (sub_url, file_name) VALUES ('http://www.google.com','aaa');")
                                c.execute("INSERT INTO " + domain.replace('.', '_') + " (urls, file_name) VALUES (?,?)",
                                          (link, unquote(link).split("/")[-1]))
                                conn.commit()

                    if (link not in new_links and link not in pdf_links):
                        flag = 1
                        for not_file_type in not_file_types:
                            if (not_file_type in link):
                                flag = 0

                        if (flag):
                            new_links.append(link)

    extractLinks(content)


# First scrape
scrapeIt(url)

# Second time scrape
for i in new_links:
    print(i + " : " + str(len(new_links)))
    scrapeIt(i)

print("completed!")
conn.close()
