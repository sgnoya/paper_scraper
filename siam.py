# %%
import datetime
import os
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf

from utils import discord, init_twitterapi

today = datetime.datetime.today()
today = today.replace(hour=8, minute=0, second=0, microsecond=0)
yesterday = today + datetime.timedelta(days=-1)

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))
subscribe = OmegaConf.load(os.path.join(cwd, "subscribe.yml"))

twkeys = keys.twitter.app
twapi = init_twitterapi(
    twkeys.apikey, twkeys.apisecret, twkeys.token, twkeys.tokensecret
)
urls = subscribe.siam.urls

with open(os.path.join(cwd, "siam.csv"), "r") as f:
    data = f.readlines()
sent = []

# %%
for url in urls:
    # Get the list of papers
    msg = None

    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode(), "html.parser")
    docs = soup.find_all("item")

    # get info of a paper
    for doc in docs:
        link = doc.get("rdf:about")
        title = doc.find("title").text
        date = doc.find("dc:date").text
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        date = date.replace(hour=8, minute=0, second=0, microsecond=0)

        if msg is None:
            channel = soup.find("channel")
            msg = "@here " + doc.find("dc:source").text + "\n"
            msg += channel.get("rdf:about") + "\n"
            discord(keys.discord, msg)

        # send the paper
        if (date == today or date == yesterday) and title + "\n" not in data:
            msg = "[" + doc.find("dc:source").text + "]\n"
            msg += title + "\n" + link + "\n"
            discord(keys.discord, msg)

            try:
                twapi.update_status(msg)
                sent.append(title + "\n")
            except Exception as e:
                print(e)

with open(os.path.join(cwd, "siam.csv"), "a") as f:
    f.writelines(sent)
