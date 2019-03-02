#!/usr/bin/env python3

"""Asynchronously get links embedded in multiple pages' HMTL."""

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

from urllib.parse import urlparse, urljoin
import requests

import lxml.html

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

HREF_RE = re.compile(r'href="(.*?)"')

new_links = [];
visited_links = [];
pdf_links = []

not_url = ['/', '#', 'javascript:void(0)']
file_types = ['.pdf', '.doc', '.docx', '.xlxs', '.ppt', '.pptx', '.jpg', '.png']

# main_url = 'http://www.paavam.com'
url = 'http://mhrd.gov.in/'
domain = urlparse(url).netloc


def extractLinks(content, new_url):
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
                        pdf_links.append(link)

                if (link not in new_links and link not in pdf_links):
                    new_links.append(link)


async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.
    kwargs are passed to `session.request()`.
    """
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    # logger.info("Got response [%s] for URL: %s", resp.status, url)
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

        logger.info("new_links increased to %d for %s", len(new_links), url)
        return set(new_links)


async def write_one(file: IO, url: str, **kwargs) -> None:
    """Write the found HREFs from `url` to `file`."""
    res = await parse(url=url, **kwargs)
    if not res:
        return None
    async with aiofiles.open(file, "a") as f:
        for p in res:
            await f.write(f"{url}\t{p}\n")
        logger.info("Wrote results for source URL: %s", url)


async def bulk_crawl_and_write(file: IO, **kwargs) -> None:
    """Crawl & write concurrently to `file` for multiple `urls`."""
    async with ClientSession() as session:
        tasks = []
        for url in new_links:
            tasks.append(
                write_one(file=file, url=url, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    # TODO: Accept only single link
    my_url = 'http://mhrd.gov.in/'

    outpath = here.joinpath("foundurls.txt")
    with open(outpath, "w") as outfile:
        outfile.write("source_url\tparsed_url\n")

    content = requests.get(my_url).content
    extractLinks(content, my_url)

    asyncio.run(bulk_crawl_and_write(file=outpath))
