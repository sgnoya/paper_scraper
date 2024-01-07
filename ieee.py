# %%
import datetime
import os
import time

from bs4 import BeautifulSoup
from omegaconf import OmegaConf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import discord, init_twitterapi

cwd, _ = os.path.split(os.path.abspath(__file__))
with open(os.path.join(cwd, "ieee.csv"), "r") as f:
    data = f.readlines()

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
options.add_argument('window-size=1400,600')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--user-agent=Chrome/110")
options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'profile': {'password_manager_enabled': False}
})

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)


def get_class(_url, _target, _type="class"):
    driver = webdriver.Chrome(options=options)
    driver.get(_url)
    time.sleep(5)

    if _type == "class":
        elem = driver.find_element_by_class_name(_target)
    else:
        elem = driver.find_element_by_id(_target)
    soup = BeautifulSoup(elem.get_attribute("innerHTML"), "html.parser")
    driver.quit()
    return soup

def get_paper_info(url):
    driver.get(url)
    journal_title = driver.find_element(by=By.CLASS_NAME, value="title-section").text.split("\n")[0]

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elem = driver.find_elements(by=By.CLASS_NAME, value="result-item-title")

    papers = []
    for e in elem:
        soup = BeautifulSoup(e.get_attribute("innerHTML"), "html.parser")
        papers.append((soup.text, base + soup.find("a").get("href")))

    return journal_title, papers

sent = []

for url in urls:
    # Get the list of papers
    msg = None
    _url = "https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=" + str(url)
    
    journal_title, paper_info = get_paper_info(_url)
        # send the paper
    
    for title, link in paper_info:
        if title + "\n" not in data:
            sent.append(title + "\n")
            msg = "[" + journal_title + "]\n"
            msg += title + "\n" + link + "\n"
            discord(keys.discord, msg)
            try:
                twapi.update_status(msg)
            except Exception as e:
                print(e)


with open(os.path.join(cwd, "ieee.csv"), "a") as f:
    f.writelines(sent)

driver.quit()
