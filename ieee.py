# %%
import datetime
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils import discord, init_twitterapi

today = datetime.datetime.today()
t_month = today.strftime("%B")
t_year = today.strftime("%Y")
t_day = today.strftime("%d")

yesterday = today + datetime.timedelta(days=-1)
y_month = yesterday.strftime("%B")
y_year = yesterday.strftime("%Y")
y_day = yesterday.strftime("%d")

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))
subscribe = OmegaConf.load(os.path.join(cwd, "subscribe.yml"))

base = subscribe.ieee.base
urls = subscribe.ieee.urls

twkeys = keys.twitter.app
twapi = init_twitterapi(
    twkeys.apikey, twkeys.apisecret, twkeys.token, twkeys.tokensecret
)

options = Options()
options.add_argument("--headless")


def get_class(_url, _target, _type="class"):
    driver = webdriver.Chrome(options=options)
    driver.get(_url)
    if _type == "class":
        elem = driver.find_element_by_class_name(_target)
    else:
        elem = driver.find_element_by_id(_target)
    time.sleep(5)  # FIXME:
    soup = BeautifulSoup(elem.get_attribute("innerHTML"), "html.parser")
    driver.quit()
    return soup


for url in urls:
    # Get the list of papers
    msg = None
    _url = "https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=" + str(url)
    soup = get_class(
        _url,
        "global-content-wrapper",
        "class",
    )
    docs = soup.find_all("a")
    docs = [doc.get("href") for doc in docs]  # all link
    docs = [doc for doc in docs if doc is not None]
    docs = list(
        set(
            [
                doc
                for doc in docs
                if "document" in doc and "?" not in doc and "#" not in doc
            ]
        )
    )  # only paper links
    print(docs)

    # get info of a paper
    for doc in docs:
        soup = get_class(base + doc, "LayoutWrapper", "id")
        target = None
        # search meta data
        for i in soup.find_all("script", type="text/javascript"):
            if i.string is not None:
                if "xplGlobal.document.metadata" in i.string:
                    target = i
                    break

        meta = re.search(
            r"xplGlobal.document.metadata\=\{.+?\};", target.decode()
        )
        meta = meta.group()
        meta = re.sub(";", "", meta)
        meta = re.sub("xplGlobal.document.metadata\=", "", meta)

        dic = json.loads(meta)
        title = dic["formulaStrippedArticleTitle"]
        date = dic["onlineDate"]
        link = dic["doiLink"]

        if msg is None:
            msg = "@here " + dic["publicationTitle"] + "\n"
            msg += _url + "\n"
            discord(keys.discord, msg)

        # send the paper
        day, month, year = date.split(" ")
        if (int(day) == int(t_day) and month == t_month and year == t_year) or (
            int(day) == int(y_day) and month == y_month and year == y_year
        ):
            msg = "[" + dic["publicationTitle"] + "]\n"
            msg += title + "\n" + link + "\n"
            discord(keys.discord, msg)
            try:
                twapi.update_status(msg)
            except Exception as e:
                print(e)
