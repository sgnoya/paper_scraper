# %%
import os
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf

from utils import discord, init_twitterapi

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))

twkeys = keys.twitter.app
twapi = init_twitterapi(
    twkeys.apikey, twkeys.apisecret, twkeys.token, twkeys.tokensecret
)


with open(os.path.join(cwd, "jmlr.csv"), "r") as f:
    data = f.readlines()

sent = []

url = "https://www.jmlr.org/"
response = requests.get(url)
soup = BeautifulSoup(response.content.decode(), "html.parser")
docs = soup.find_all("dl")

# %%
discord(keys.discord, "@here JMLR \n")
time.sleep(2)
msg = ""

for i, doc in enumerate(docs):

    title = doc.find("dt").text
    link = doc.find_all("a")
    link = url + [i.get("href") for i in link if "pdf" in i.get("href")][0]

    if title + "\n" not in data:
        msg += title + "\n" + link + "\n"
        sent.append(title + "\n")

        _msg = "[JMLR] "
        _msg += title + "\n" + link + "\n"
        try:
            twapi.update_status(_msg)
        except Exception as e:
            print(e)

    if (i + 1) % 9 == 0:
        discord(keys.discord, msg + "\n")
        msg = ""

discord(keys.discord, msg + "\n")

with open(os.path.join(cwd, "jmlr.csv"), "a") as f:
    f.writelines(sent)
