

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
            anchorList = anchorList + (soupHtml.find_all("a",attrs={'class':'link_txt'}))


        for anchorData in anchorList:
            response.append({'title':anchorData.text, 'href':anchorData['href']})

        return response
    def parseArticle(self,url):
        data = requests.get(url)
        ArticleHtml = BeautifulSoup(data.text, 'html.parser')

        response = ArticleHtml.find('div',attrs={'id':'harmonyContainer'})
        return response.text

