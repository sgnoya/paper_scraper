# %%
import os
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf

from utils import discord, init_twitterapi

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))
subscribe = OmegaConf.load(os.path.join(cwd, "subscribe.yml"))

journals = subscribe.springer.journals
base = subscribe.springer.base

twkeys = keys.twitter.app
twapi = init_twitterapi(
    twkeys.apikey, twkeys.apisecret, twkeys.token, twkeys.tokensecret
)

with open(os.path.join(cwd, "springer.csv"), "r") as f:
    data = f.readlines()

sent = []

for journal in journals:
    url = "https://link.springer.com/search.rss?facet-journal-id=" + str(journal)
    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode(), "xml")

    docs = soup.find_all("item")

    journal_info = docs[0]
    journal_name = journal_info.title.text

    msg = "@here (Springer)" + journal_name + "\n"
    discord(keys.discord, msg)

    docs = docs[1:]
    msg = ""
    for i, doc in enumerate(docs):
        link = doc.link.text
        title = doc.title.text

        if title + "\n" not in data:
            msg += title + "\n" + link + "\n"

            _msg = "[Springer: " + journal_name + "]\n"
            _msg += title + "\n" + link + "\n"
            try:
                twapi.update_status(_msg)
                sent.append(title + "\n")
            except Exception as e:
                print(e)

        if (i + 1) % 9 == 0:
            discord(keys.discord, msg + "\n")
            msg = ""

    discord(keys.discord, msg + "\n")

with open(os.path.join(cwd, "springer.csv"), "a") as f:
    f.writelines(sent)

# %%
