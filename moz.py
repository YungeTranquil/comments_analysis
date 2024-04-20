import requests
import requests_cache
import json
import sys
import os

from bs4 import BeautifulSoup

requests_cache.install_cache('moz',backend='filesystem')


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

def moz_cookie_manage():
    """save cookie from https://moz.com/domain-analysis"""
    with open("moz-2.json","r") as file:
        cookies = json.loads(file.read())
        cookies = cookies["cookies"]
    return cookies

def queryMoz(domain,cache_disable=False):


    url = f"https://moz.com/domain-analysis?site={domain}"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": user_agent}
    cookies = moz_cookie_manage()

    cookies_moz = {cookie["name"]:cookie["value"] for cookie in cookies}
    columns = ["Domain Authority","Linking Root Domains","Ranking Keywords","Spam Score"]
    if cache_disable:
         with requests_cache.disabled():
            response = fetchUrl(url,cookies=cookies_moz)
    else:
        response = fetchUrl(url,cookies=cookies_moz)
    with open("data/moz_last_test.html","w",encoding="utf-8") as file:
        file.write(response.text)
    output_list = [item.text for item in BeautifulSoup(response.content, features="lxml").find_all("h1")[1:]]
    return {key:value for key,value in zip(columns,output_list)}
        #else:
         #   print("Cookies Expired")
        
def create_session():
    """
    Create a session object with a custom User-Agent to persist cookie state.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    return session

def query_moz(domain, session):
    """
    Query Moz for domain analysis, using a session to maintain cookie state.
    """
    url = f"https://moz.com/domain-analysis?site={domain}"
    
    # Use the session to make a GET request
    response = session.get(url)
    
    # Check the response status
    if response.status_code != 200:
        print(f"Failed to fetch {url}: Status code {response.status_code}")
        return None

    # Parse the HTML content using BeautifulSoup if needed
    soup = BeautifulSoup(response.text, 'html.parser')
    output_list = [item.text for item in BeautifulSoup(response).find_all("h1")[1:]]
        #output_list = [item.text for item in BeautifulSoup(response.text).find_all("h1")[1:]]
        #if len(output_list) != 0:
    columns = ["Domain Authority","Linking Root Domains","Ranking Keywords","Spam Score"]
    if output_list:
        return {key:value for key,value in zip(columns,output_list)}
    
if __name__ == "__main__":
    url = sys.argv[1]
    result = queryMoz(url)
    if result == {}:
        result = queryMoz(url,cache_disable=True)
    print(result)