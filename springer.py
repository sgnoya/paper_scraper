# %%
import os
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))
subscribe = OmegaConf.load(os.path.join(cwd, "subscribe.yml"))

journals = subscribe.springer.journals
base = subscribe.springer.base

with open(os.path.join(cwd, "springer.csv"), "r") as f:
    data = f.readlines()


def discord(message):
    url = keys.discord
    payload = {"content": message}

    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        return s.post(url, data=payload)


sent = []

for journal in journals:
    url = (
        "https://link.springer.com/search?query=&search-within=Journal&facet-journal-id="
        + str(journal)
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode(), "html.parser")
    docs = soup.find_all("a", class_="title")

    msg = (
        "@here (Springer)"
        + soup.find("p", class_="title").text.replace("\n", "")
        + "\n"
    )
    discord(msg)
    time.sleep(2)

    msg = ""
    for i, doc in enumerate(docs):
        link = base + doc.get("href")
        title = doc.text.replace("\n", "")

        if title + "\n" not in data:
            msg += title + "\n" + link + "\n"
            sent.append(title + "\n")

        if (i + 1) % 9 == 0:
            discord(msg + "\n")
            time.sleep(2)
            msg = ""

    discord(msg + "\n")
    time.sleep(2)

with open(os.path.join(cwd, "springer.csv"), "a") as f:
    f.writelines(sent)
