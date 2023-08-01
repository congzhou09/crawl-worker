import re
import random
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import trafilatura

from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

from common.logger.logger import logger


# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

error_url = []

WAIT_SEC = 3  # wait randomly [1, WAIT_SEC] seconds  between each page crawling


################################################################################
### Step 1
################################################################################
def fetchDynamic(one_url):
    wait_sec_final = 0
    if WAIT_SEC > 0:
        wait_sec_final = WAIT_SEC + random.randint(1, WAIT_SEC)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(one_url, wait_until="load")
        if wait_sec_final > 0:
            page.wait_for_timeout(wait_sec_final * 1000)
        html_text = page.content()
        browser.close()
        return html_text


# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])


################################################################################
### Step 2
################################################################################


# Function to get the hyperlinks from a URL
def get_hyperlinks(url, html_text=None):
    if html_text is None:
        # Try to open the URL and read the HTML
        try:
            # Open the URL and read the HTML
            html = fetchDynamic(url)
        except Exception as e:
            logger.error(f"error get links from {url}: {e}")
            error_url.append(url)
            logger.warn(f"error urls now: {error_url}")
            return []
    else:
        html = html_text

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


################################################################################
### Step 3
################################################################################


# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url, html_text):
    clean_links = []
    for link in set(get_hyperlinks(url, html_text)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
                clean_link = "https://" + local_domain + "/" + link
            elif link.startswith("./") or link.startswith("../"):
                clean_link = urljoin(url, link)
            else:
                logger.info(f'skip: {link}')
                continue

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


################################################################################
### Step 4
################################################################################


def fetchStatic(one_url):
    return trafilatura.fetch_url(one_url)


def get_file_name(local_domain, url):
    return (
        'text/'
        + local_domain
        + '/'
        + url[8:].replace("/", "`").replace("?", "~")
        + ".txt"
    )


# Create a queue to store the URLs to crawl
queue = deque([])

# Create a set to store the URLs that have already been seen (no duplicates)
seen = set([])


# check wheather url named files have existed
def filter_err_urls(local_domain, input_error_url):
    url_remained = []
    for one_url in input_error_url:
        filename = get_file_name(local_domain, one_url)
        filesize = None
        try:
            filesize = os.path.getsize(filename)
        except:
            pass
        if filesize is None or filesize <= 0:
            url_remained.append(one_url)
    return url_remained


def record_url(one_url):
    queue.append(one_url)
    seen.add(one_url)


def refine_url(one_url):
    url_obj = urlparse(one_url)
    url_path = url_obj.path
    if len(url_path) > 0 and url_path[-1] == "/":
        url_path = url_path[0:-1]
    return url_obj.scheme + "://" + url_obj.netloc + url_path


def crawl(url, wait_sec=0):
    global error_url
    global WAIT_SEC
    WAIT_SEC = wait_sec
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    url = refine_url(url)
    record_url(url)

    # Create a directory to store the text files
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/" + local_domain + "/"):
        os.mkdir("text/" + local_domain + "/")

    # Create a directory to store the csv files
    if not os.path.exists("processed"):
        os.mkdir("processed")

    # While the queue is not empty, continue crawling
    while queue:
        # Get the next URL from the queue
        url = queue.pop()
        logger.info(url)  # for debugging and to see the progress

        html_text = None

        # Save text from the url to a <url>.txt file
        filename = get_file_name(local_domain, url)

        # for run-again case
        if not os.path.exists(filename):
            text = None
            try:
                html_text = fetchDynamic(url)
                text = trafilatura.extract(html_text)
            except Exception as exp:
                logger.error(f"error when fetching or extract {url}: {exp}")
                error_url.append(url)
                logger.warn(f"error urls: {error_url}")

            try:
                with open(filename, "w", encoding="UTF-8") as f:
                    if text is not None:
                        f.write(text)
                        f.close()
                    else:
                        f.close()
                        os.remove(filename)
            except Exception as exp:
                logger.error(f"error operating files, filename:{filename}, url: {url}")
                error_url.append(url)
                logger.warn(f"error urls: {error_url}")

            # Get the hyperlinks from the URL and add them to the queue
            for link in get_domain_hyperlinks(local_domain, url, html_text):
                refined_link = refine_url(link)
                if refined_link not in seen:
                    record_url(refined_link)
                else:
                    logger.info(f"skip: {link}, because of existed")
        else:
            logger.info(f"skip: {url}, because of existed")

    error_url = filter_err_urls(local_domain, error_url)
    if len(error_url) > 0:
        logger.warn(f"error urls final: {error_url}")


def filter_files(dir_name):
    for name in os.listdir(dir_name):
        full_name = dir_name + "/" + name
        if os.path.isfile(full_name):
            match = re.search(r"#.*(?=\.)", name)
            if match is not None:
                match_span = match.span()
                check_name = (
                    dir_name + "/" + name[0 : match_span[0]] + name[match_span[1] :]
                )
                if os.path.exists(check_name):
                    os.remove(full_name)
