import os
import sys
import time
import json
import copy
import requests

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from tqdm import tqdm

from urllib.parse import urlparse, urlunparse
import requests_cache
from bs4 import BeautifulSoup



requests_cache.install_cache('cached/news',backend='filesystem')

import newspaper

def parseWebsite(url):
    return urlparse(url).netloc

def count_links(html, base_url):
   #temp_url = urlparse(base_url)
   #domain = temp_url.scheme+"://"+temp_url.netloc
   #domain_list = domain.split(".")
   #if len(domain_list)==2:
   #    root_domain = domain_list[0]
   #else:
   #    root_domain = domain_list[1]
    
    soup = BeautifulSoup(html, 'html.parser')
    #article = soup.find_all(['p',"ul"])  # 查找所有带href的<a>标签
    article = soup.find_all(['p']) 
    
    internal_links = 0
    external_links = 0
    internal_links_list = []
    external_links_list = []

    for p in article:
        a_ = p.find_all("a", href=True)
        for link in a_:
            href = link['href']
            if href.startswith('/'):
                internal_links_list.append(href)
            elif href.startswith('http'):
                if (base_url in href):
                    internal_links_list.append(href)
                else:
                    external_links_list.append(href)
        # 添加更多的条件来更精确地分类链接
    dedup_external_links = set(map(parseWebsite,external_links_list))

    return list(set(internal_links_list)), list(set(dedup_external_links)),len(set(internal_links_list)),len(set(external_links_list)),len(set(dedup_external_links)),list(dedup_external_links)

def handleUrlList(url_list):
    output = []
    
    for url in tqdm(url_list):
        
        try:
            response = fetchUrl(url)
            url_parsed = parseWebsite(url)
            article = newspaper.article(f"{url}", input_html=response.content, language='en')
            _,_,b,c,d,e = count_links(article.article_html, f"{url_parsed}")
            
            author = article.authors
            publishdate = pd.Timestamp(article.publish_date).strftime(format="%h %d, %Y")
            
            info_dict = {"url":url,"status":response.status_code,"author":author,"publishdate":publishdate,"Internal links":b,"External links":c,"dedup external":d,"deexter":e}
            # print(f"{url} 内链数量{b} 外链数量{d}")
        except:
            info_dict = {"url":url,"status":response.status_code,"author":author,"publishdate":publishdate,"Internal links":None,"External links":None,"dedup external":None,"deexter":None}
            
        output.append(info_dict)
        with open("output.json","a",encoding="utf-8") as file:
            file.write(json.dumps(info_dict))
    return output

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

def article_parser(url,method="spider"):
    if method == "spider":
        response = fetchUrl(url)
    else:
        with open(url,"r") as file:
            response = file.read()
    
    url_parsed = parseWebsite(url)
    domain = urlparse(url)
    domain = domain.scheme +"://"+ domain.netloc
    
    article = newspaper.article(f"{url}", input_html=response.content, language='en')
    inter_links,exter_link,b,c,d,e = count_links(article.article_html, f"{url_parsed}")
    info_dict = {"url":url,"status":response.status_code,"Internal links":b,"External links":c,
                 "Non-duplicated External Links Count":d,"Non-duplicated External Links":e}
    # print(f"{url} 内链数量{b} 外链数量{d}")
    info_dict["authors"] = article.authors
    try:
        info_dict["publish_time"] = pd.Timestamp(article.publish_date).strftime("%Y-%m-%d %H:%M")
    except:
        info_dict["publish_time"] = None
    
    if len(info_dict["authors"])!= 0:
        author_pages = []
        for author in info_dict["authors"]:
            for a in BeautifulSoup(response.text).find_all("a"): 
                href_authors = "-".join(author.lower().split()[:2])
                try:
                    if href_authors in a.attrs["href"]:
                        urlparsed = urlparse(a.attrs["href"])
                        if urlparsed.netloc == "":
                            urlparsed = domain + urlparsed.path
                        else:
                            urlparsed = "https://" + urlparsed.netloc + urlparsed.path
                        author_pages.append(urlparsed)
                        break
                except:
                    continue
        if len(author_pages) != 0:
            info_dict["authors_page"] = author_pages
        else:
            info_dict["authors_page"] = None

    info_dict["sentence_counts"] = len(article.text.split("."))
    info_dict["word_counts"] = len(article.text.split())
    
    info_dict_copy = copy.deepcopy(info_dict)
    for key,value in info_dict.items():
        try:
            if (type(value)==list) & (len(value)==1):
                info_dict_copy[key] = value[0]
        except:
            continue
    return info_dict_copy


if __name__ == "__main__":
    url = sys.argv[1]
    print(article_parser(url))