import os
import sys
import time
import json
import requests

import numpy as np
import pandas as pd
from tqdm import tqdm

from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def fetchUrl(url,cookies=None):
    """
    Fetches content from a URL using a GET request with custom User-Agent and cookies.
    """
    # Ensure headers and cookies are dictionaries, if not provided, initialize as empty dicts
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": user_agent}
    if cookies is None:
        cookies = {}
    
    # Perform the GET request
    response = requests.get(url, headers=headers, cookies=cookies)
    
    return response

def start_browser():
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-javascript')
    
    browser = webdriver.Chrome(options=options)

    browser.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
    #browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #  "source": """
    #    Object.defineProperty(navigator, 'webdriver', {
    #      get: () => undefined
    #    })
    #  """
    #})
    #browser.execute_cdp_cmd("Network.enable", {})
    #browser.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
    return browser

def queryGoogle(browser,keyword,method=1):
    if method == 1:
        browser.get(f"https://www.google.com/search?q={keyword}&ie=UTF-8&tbm=nws&hl=en&tbs=qdr:y")
    else:
        browser.get(f"https://www.google.com/")
    
def nextPageGoogle(browser):
    alist = browser.find_elements(By.CSS_SELECTOR,"a")
    alist.reverse()
    for a in alist:
        if ("Next" in a.text) | ("下一页" in a.text)|(">" in a.text):
            button = a
    button.click()

def pageResultGoogle(browser):
    response = BeautifulSoup(browser.page_source)
    result = response.find_all("div",attrs={"id":"main"})[0]
    search_results = [content for content in result.find_all("div",recursive=False) if len(content.find_all("h3"))!=0]
    search_list_dict = []
    for search_result in search_results:
        title,brand,descript = [div.text for div in search_result.find_all("div") if (len(div.find_all("div"))==0)&(len(div.text)!=0)]
        urls = search_result.a.attrs["href"].split("&")
        for item in urls:
            if "url" in item:
                url = item[4:]
        time = search_result.span.text
        temp_dict = {"title":title,"brand":brand,"descript":descript,"url":url,"time":time}
        search_list_dict.append(temp_dict)
    return search_list_dict

def cookieGoogle(browser,domain=None,method="read"):
    if method == "save":
        temp_cookies = browser.get_cookies()
        domain = temp_cookies[0]["domain"].split(".")[-2]
        with open(f"config/cookies_{domain}.json","w",encoding="utf-8") as file:
            file.write(json.dumps(temp_cookies))
    else:
        if domain != None:
            domain = urlparse(browser.current_url).netloc.split(".")[-2]
        if f"cookies_{domain}.json" not in os.listdir("config"):
            return "Cookies Not Existed"
        else:
            with open(f"config/cookies_{domain}.json","r",encoding="utf-8") as file:
                cookies = json.loads(file.read())
        for cookie in cookies:
            browser.add_cookie(cookie)

def tryUrl(url):
    parsed_url = urlparse(url)
    parsed_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "/".join(parsed_url.path.split("/")[:-1]), '', '',''))
    return parsed_url

def dataframe_to_mysql(df, table_name, database_url):

    database_url = "mysql+pymysql://root:a1258896@1.tcp.cpolar.cn:24150/spider"
    table_name = 'google_search'
    # 创建数据库引擎
    engine = create_engine(database_url)
    
    # 使用to_sql方法上传DataFrame
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    
    # print(f"DataFrame uploaded to `{table_name}` table in the database.")