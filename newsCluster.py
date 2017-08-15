import hashlib

from konlpy.tag import Mecab
from math import log, sqrt


class NewsCluster:
    def __init__(self):
        self.trash = 0
        self.nlpWorker = Mecab()

    def extractTf(self,article):
        afterNLP = self.nlpWorker.nouns(article)

        newsNode = NewsNode()
        newsNode.article = article
        for element in afterNLP:
            newsNode.__add__(element)
        for key in newsNode.tfMap.keys():
            newsNode.tfMap[key]['tf'] = 0.5 + 0.5 * newsNode.tfMap[key]['count'] / newsNode.countTerms

        return newsNode
    # def extractIdf(self):

    def getIdfValue(self, newsNodes, term):
        matchedCount = 0;
        for news in newsNodes:
            if term in news.tfMap.keys():
                matchedCount+=1
        return log(newsNodes.__len__() / (1+matchedCount))
    def getSimilarity(self,articleOne,articleTwo):
        groupTfMap = list(articleOne.tfMap.keys()) + list(articleTwo.tfMap.keys())
        groupTfMap = set(groupTfMap)
        docProductNumber = 0
        euclideanLenOfOne = 0
        euclideanLenOfTwo = 0
        for term in groupTfMap:
            tfidfOne = articleOne.tfMap[term]['tfidf'] if term in articleOne.tfMap.keys() else 0
            tfidfTwo = articleTwo.tfMap[term]['tfidf'] if term in articleTwo.tfMap.keys() else 0

            docProductNumber += tfidfOne * tfidfTwo
            euclideanLenOfOne += pow(tfidfOne,2)
            euclideanLenOfTwo += pow(tfidfTwo,2)
        similarity = docProductNumber / (sqrt(euclideanLenOfOne) * sqrt(euclideanLenOfTwo))
        return similarity





class NewsNode:
    def __init__(self):
        self.countTerms = 0
        self.article = ''
        self.tfMap = {}
    def __add__(self, element):
        if element in self.tfMap.keys():
            self.tfMap[element]['count'] = self.tfMap[element]['count'] + 1
        else:
            self.tfMap[element] = {'count': 1}
        self.countTerms += 1
