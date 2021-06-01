# %%
import os
import time

import requests
from bs4 import BeautifulSoup
from omegaconf import OmegaConf

cwd, _ = os.path.split(os.path.abspath(__file__))
keys = OmegaConf.load(os.path.join(cwd, "keys.yml"))

with open(os.path.join(cwd, "jmlr.csv"), "r") as f:
    data = f.readlines()

def discord(message):
    url = keys.discord
    payload = {"content": message}

    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        return s.post(url, data=payload)

sent = []

url = "https://www.jmlr.org/"
response = requests.get(url)
soup = BeautifulSoup(response.content.decode(), "html.parser")
docs = soup.find_all("dl")

# %%
msg = ""
for i, doc in enumerate(docs):
    title = doc.find("dt").text
    link = doc.find_all("a")
    link = url + [i.get("href") for i in link if "pdf" in i.get("href")][0]

    if title + "\n" not in data:
        msg += title + "\n" + link + "\n"
        sent.append(title + "\n")

    if (i + 1) % 9 == 0:
        discord(msg + "\n")
        time.sleep(2)
        msg = ""

discord(msg + "\n")
time.sleep(2)

with open(os.path.join(cwd, "jmlr.csv"), "a") as f:
    f.writelines(sent)
