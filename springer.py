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
    url = (
        "https://link.springer.com/search?query=&search-within=Journal&facet-journal-id="
        + str(journal)
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode(), "html.parser")
    docs = soup.find_all("a", class_="title")
    journal_name = soup.find("p", class_="title").text.replace("\n", "")
    msg = "@here (Springer)" + journal_name + "\n"
    discord(keys.discord, msg)
    time.sleep(2)

    msg = ""
    for i, doc in enumerate(docs):
        link = base + doc.get("href")
        title = doc.text.replace("\n", "")

        if title + "\n" not in data:
            msg += title + "\n" + link + "\n"
            sent.append(title + "\n")

            _msg = "[Springer: " + journal_name + "]\n"
            _msg += title + "\n" + link + "\n"
            twapi.update_status(_msg)
            time.sleep(0.1)

        if (i + 1) % 9 == 0:
            discord(keys.discord, msg + "\n")
            time.sleep(2)
            msg = ""

    discord(keys.discord, msg + "\n")
    time.sleep(2)

with open(os.path.join(cwd, "springer.csv"), "a") as f:
    f.writelines(sent)
