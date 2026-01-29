import os
import requests
import json
import jieba
import re
from bs4 import BeautifulSoup

from datetime import datetime, timedelta

from pkg.settings import setting as settings


def filter_date(d_time):
    date_now = datetime.today()
    date_delta = datetime.today() - timedelta(days = settings.DAY_BEFORE)
    return (date_delta < d_time < date_now)


def get_links(url):
    """
    抓取文章列表頁面，取得符合日期條件的文章連結
    新版網站結構：使用 <time> 標籤和文章連結配對
    """
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []

    # 找出所有文章連結（格式: /article/數字）
    article_links = soup.find_all('a', href=re.compile(r'/article/\d+'))

    # 用 set 去重
    processed_hrefs = set()

    for link in article_links:
        href = link.get('href')

        # 避免重複處理同一個連結
        if href in processed_hrefs:
            continue

        # 轉換為完整 URL
        if not href.startswith('http'):
            full_url = 'https://www.thenewslens.com' + href
        else:
            full_url = href

        # 往上找父元素中的日期標籤
        parent = link.parent
        date_found = False

        for _ in range(10):  # 最多往上找 10 層
            if parent:
                time_elem = parent.find('time')
                if time_elem:
                    try:
                        time_text = time_elem.get_text(strip=True)
                        news_datetime = datetime.strptime(time_text, "%Y/%m/%d")

                        # 檢查日期是否在範圍內
                        if filter_date(news_datetime):
                            links.append(full_url)
                            processed_hrefs.add(href)

                        date_found = True
                        break
                    except Exception:
                        pass

                parent = parent.parent
            else:
                break

        # 如果找不到日期但連結有效，也加入（為了容錯）
        if not date_found and href not in processed_hrefs:
            # 可選：是否要包含沒有日期的文章
            # links.append(full_url)
            # processed_hrefs.add(href)
            pass

    return links


def get_content(link):
    """
    抓取單篇文章的標題和內容
    支援多種內容容器選擇器以提高穩健性
    """
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, "html.parser")
    link_id = link.split("/")[-1]

    # 抓取標題
    title_elem = soup.select_one("title")
    if title_elem:
        title = title_elem.text.strip(" - The News Lens 關鍵評論網").strip(" - 第 1 頁").strip()
    else:
        title = "無標題"

    # 抓取內容 - 嘗試多種選擇器
    content = ""
    content_selectors = [
        "div.article-body-container",  # 舊版選擇器
        "article",                     # 新版可能使用 article 標籤
        "div.article-content",
        "div[class*='article-body']"
    ]

    for selector in content_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            paragraphs = content_elem.findAll("p")
            if paragraphs:
                content = "".join([p.text.strip() for p in paragraphs])
                break

    # 如果都找不到內容，至少記錄一個空字串
    if not content:
        content = ""

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

