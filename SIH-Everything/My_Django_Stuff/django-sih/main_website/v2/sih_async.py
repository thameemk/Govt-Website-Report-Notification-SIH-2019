#!/usr/bin/env python3

"""Asynchronously get links embedded in multiple pages' HMTL."""

def asyncScraping(url):
    import asyncio
    import logging
    import re
    import sys
    from typing import IO
    import urllib.error
    import urllib.parse

    import aiofiles
    import aiohttp
    from aiohttp import ClientSession

    from urllib.parse import urlparse, urljoin, unquote
    import requests

    import lxml.html
    import sqlite3
    import pathlib

    from . import mail_sender

    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    # url = 'http://mhrd.gov.in/'
    domain = urlparse(url).netloc

    outpath = here.joinpath("new_urls_%s" % (domain))
    with open(here.joinpath("new_urls_%s.txt" % (domain))) as infile:
        urls = set(map(str.strip, infile))

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    logger = logging.getLogger('chardet.charsetprober')
    logger.setLevel(logging.INFO)
    logging.getLogger("chardet.charsetprober").disabled = True

    HREF_RE = re.compile(r'href="(.*?)"')

    # new_links = []
    # previous_links = []
    pdf_links = []

    not_url = ['/', '#', 'javascript:void(0)']
    file_types = ['.pdf', '.PDF']

    here = pathlib.Path(__file__).parent
    outpath = here.joinpath("govt_db.db")

    conn = sqlite3.connect(str(outpath))
    c = conn.cursor()

    # Create table
    try:
        c.execute("SELECT urls FROM {url}".format(url=domain.replace('.', '_')))
        data = c.fetchall()
        for i in range(len(data)):
            pdf_links.append(list(data[i])[0])

        print(pdf_links)

    except sqlite3.OperationalError as e:
        print('[-] Sqlite operational error: {} Retrying...'.format(e))

    def some_function(i):
        if (i not in pdf_links):
            print("[-] New links found!!!..." + i)
            with open(here.joinpath("new_urls_%s.txt" % (domain)), "a") as f:
                f.write(f"{i}\n")
            print("Wrote results for source URL: %s" % (i))

    def extractLinks(content, new_url):
        print("I am here teena 1")
        dom = lxml.html.fromstring(content.encode("utf8"))
        # print("" + new_url + " : " + str(len(dom.xpath('//a/@href'))))
        for link in dom.xpath('//a/@href'):
            print("I am here teena 2")
            # retun if '#' and links
            if (link not in not_url):
                # convert '/gallery' to full link "https://../gallery"
                if (urlparse(link).scheme != urlparse(new_url).scheme):
                    link = urljoin(new_url, link)

                # check for same domain links
                if (urlparse(link).netloc == domain):
                    print("I am here teena 3")
                    # removing link parameters
                    # if ('#' in link or '?' in link or '&' in link):
                    #     link = urljoin(url, urlparse(link).path)

                    for file_type in file_types:
                        if (file_type in link and link not in pdf_links):
                            if (requests.get(link).status_code != 404):
                                pdf_links.append(link)
                                # Insert a row of data and commit
                                c.execute("INSERT INTO " + domain.replace('.',
                                                                          '_') + " (urls, file_name,source_url) VALUES (?,?,?)",
                                          (link, unquote(link).split("/")[-1], new_url))
                                some_function(link)
                                mail_sender.sendMailMultiple(link, unquote(link).split("/")[-1])
                                print("blahhhed: " + link)
                                print("I am here teena 4")

    async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
        """GET request wrapper to fetch page HTML.
        kwargs are passed to `session.request()`.
        """
        resp = await session.request(method="GET", url=url, **kwargs)
        resp.raise_for_status()
        logger.info("Got response [%s] for URL: %s", resp.status, url)
        html = await resp.text()
        return html

    async def parse(url: str, session: ClientSession, **kwargs) -> set:
        """Find HREFs in the HTML of `url`."""
        found = set()
        try:
            html = await fetch_html(url=url, session=session, **kwargs)
        except (
                aiohttp.ClientError,
                aiohttp.http_exceptions.HttpProcessingError,
        ) as e:
            logger.error(
                "aiohttp exception for %s [%s]: %s",
                url,
                getattr(e, "status", None),
                getattr(e, "message", None),
            )
            return found
        except Exception as e:
            logger.exception(
                "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
            )
            return found
        else:
            extractLinks(html, url)

            # logger.info("new_links increased to %d for %s", len(new_links), url)
            return set(new_links)

    async def write_one(file: IO, url: str, **kwargs) -> None:
        """Write the found HREFs from `url` to `file`."""
        res = await parse(url=url, **kwargs)
        if not res:
            return None

    async def bulk_crawl_and_write(file: IO, urls: set, **kwargs) -> None:
        """Crawl & write concurrently to `file` for multiple `urls`."""
        async with ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(
                    write_one(file=file, url=url, session=session, **kwargs)
                )
            await asyncio.gather(*tasks)

    while(1):
        asyncio.run(bulk_crawl_and_write(file=outpath, urls=urls))
    conn.commit()
