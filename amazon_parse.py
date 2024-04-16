from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import os

def parse_page(path):
    with open(f"{path}","r",encoding="utf-8") as file:
        response = file.read()
    response = BeautifulSoup(response)

    title = response.find("span",attrs={"id":"productTitle"}).text.strip()
    rate = response.find("span",attrs={"id":"acrPopover"}).span.a.span.text.strip()
    rate_number = response.find("span",attrs={"id":"acrCustomerReviewText"}).text.strip()
    sold_number = response.find("span",attrs={"id":"social-proofing-faceout-title-tk_bought"}).span.text.strip()
    description = response.find("div",attrs={"id":"feature-bullets"}).ul.text
    rate_dist = [tr.text for tr in response.select("#cm_cr_dp_d_rating_histogram")[0].find_all("tr")]
    ai_comment = response.select("#product-summary")[0].text
    keyword_comments = response.select("#cr-product-insights-cards > div:nth-child(2) > div.a-section.a-spacing-mini._cr-product-insights_style_sentiment-section__6zKPq > div ")[0].find_all("span")
    keyword_comments = [span.text for span in keyword_comments]
    nav = " ".join([li.text.strip() for li in response.select("#wayfinding-breadcrumbs_feature_div > ul > li")])
    user_reviews = response.find_all("div",attrs={"id":"cm-cr-dp-review-list"})[0].text

    product_info = {
        "title": title,
        "rate": rate,
        "rate_number": rate_number,
        "sold_number": sold_number,
        "description": description,
        "rate_dist": rate_dist,
        "ai_comment": ai_comment,
        "keyword_comments": keyword_comments,
        "nav": nav,
        "user_reviews":user_reviews
    }

    return product_info

if __name__ == "__main__":
    output = []
    url_list = os.listdir("data/amazon_html")
    for url in tqdm(url_list):
        try:
            result = parse_page(f"data/amazon_html/{url}")
            output.append(result)
        except:
            continue

    pd.DataFrame(output).to_csv("amazon_us.csv")