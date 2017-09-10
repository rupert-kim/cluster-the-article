

from bs4 import BeautifulSoup
import requests
from konlpy.tag import Mecab
import sys

mecab = Mecab()
URL = "http://media.daum.net/breakingnews/entertain?"
URL_PAGE = "&page={}"
URL_DATE = "&regDate={}"

class DaumNewsParse:

    def __init__(self):
        self.data = 0

    def parseUrlList(self,paramDate):
        response = []
        anchorList = []
        pageIdx = 1
        for pageIdx in range(1,sys.maxsize):
            data = requests.get(URL+URL_DATE.format(paramDate)+URL_PAGE.format(pageIdx))
            data = BeautifulSoup(data.text,"html.parser")

            if data.find('p',attrs={'class':'txt_none'}) is not None:
                break

            soupHtml = data.find("ul", attrs={'class': 'list_news2 list_allnews'})
            listHtml = soupHtml.find_all("li")


            anchorList = anchorList + listHtml


        for anchorData in anchorList:
            object = {}
            img = anchorData.find("img",attrs={'class':'thumb_g'})
            if img is None:
                img = ''
            else:
                img = img['src']
            anchor = anchorData.find("a", attrs={'class': 'link_txt'})

            response.append({'title': anchor.text, 'thumb': img,'href': anchor['href']})

        return response
    def parseArticle(self,url):
        data = requests.get(url)
        ArticleHtml = BeautifulSoup(data.text, 'html.parser')

        failedData = ArticleHtml.find('div',attrs={'class':'empty_view'})
        if failedData is not None:
            return None

        response = ArticleHtml.find('div',attrs={'id':'harmonyContainer'})
        return response.text

