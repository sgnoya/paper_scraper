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

journals = subscribe.elsevier.journals

twkeys = keys.twitter.app
twapi = init_twitterapi(
    twkeys.apikey, twkeys.apisecret, twkeys.token, twkeys.tokensecret
)

with open(os.path.join(cwd, "elsevier.csv"), "r") as f:
    data = f.readlines()

sent = []

for journal in journals:
    response = requests.get(
        "https://www.journals.elsevier.com/" + journal + "/recent-articles"
    )
    soup = BeautifulSoup(response.content.decode(), "html.parser")
    docs = soup.find_all("div", class_="pod-listing")

    msg = "@here (Elsevier)" + journal + "\n"
    discord(keys.discord, msg)
    time.sleep(2)

    msg = ""
    for i, doc in enumerate(docs):
        meta = doc.find("a")
        title = meta.get("title")
        link = meta.get("href")

        if title + "\n" not in data:
            msg += title + "\n" + link + "\n"
            sent.append(title + "\n")

            _msg = "[Elsevier: " + journal + "]\n"
            _msg += title + "\n" + link + "\n"
            try:
                twapi.update_status(msg)
                time.sleep(0.1)
            except Exception as e:
                print(e)

        if (i + 1) % 9 == 0:
            discord(keys.discord, msg + "\n")
            time.sleep(2)
            msg = ""

    discord(keys.discord, msg + "\n")
    time.sleep(2)


with open(os.path.join(cwd, "elsevier.csv"), "a") as f:
    f.writelines(sent)
