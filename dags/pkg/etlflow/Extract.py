import os
import requests
import json
from bs4 import BeautifulSoup
import jieba

from datetime import datetime, timedelta

from pkg.settings import setting as settings


def filter_date(d_time):
    date_now = datetime.today()
    date_delta = datetime.today() - timedelta(days = settings.DAY_BEFORE)
    return (date_delta < d_time < date_now)


def get_links(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for i in soup.select("div.info-box"):
        time = i.select_one("span.time").text.strip("|  ")
        news_datetime = datetime.strptime(time, "%Y/%m/%d")
        for gtm in i.select("a.gtm-track"):
            if (gtm.get("data-gtm-label") == "title"):
                link = gtm.get("href")
            else:
                pass
        if filter_date(news_datetime):
            links.append(link)
    return links


def get_content(link):
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, "html.parser")
    link_id = link.split("/")[-1]
    title = soup.select_one("title").text.strip(" - The News Lens 關鍵評論網")
    content = "".join([i.text.strip() for i in soup.select_one("div.article-body-container").findAll("p")])
    news = {
        "link_id": link_id,
        "title": title,
        "content": content
    }
    return news


def main():
    path = os.path.join(settings.SRC_FOLDER, settings.TRANSFORMATION_INPUT)
    url = 'https://www.thenewslens.com/category/politics'
    links = get_links(url)
    os.makedirs(path, exist_ok=True)
    news_list = []
    news_path = os.path.join(path, settings.TRANSFORMATION_INPUT_FILE)
    for link in links:
        news = get_content(link)
        news_list.append(news)

    with open(news_path, "w") as f:
        json.dump(news_list, f)
    return path

