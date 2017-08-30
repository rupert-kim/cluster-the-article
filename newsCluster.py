import hashlib

from konlpy.tag import Mecab
from math import log, sqrt


class NewsCluster:
    def __init__(self):
        self.trash = 0
        self.nlpWorker = Mecab()

    def extractTf(self, article):
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
        matchedCount = 0
        for news in newsNodes:
            if term in news.tfMap.keys():
                matchedCount += 1
        # @ Critical issue : 어떠한 상황에서 idf 값이 마이너스가 나옴. 수식에서 마이너스의 가능성을 찾아보고 그에 대한 방안을 마련할 필요가 있다
        return log(newsNodes.__len__() / (1 + matchedCount))

    def getSimilarity(self, articleOne, articleTwo):
        groupTfMap = list(articleOne.tfMap.keys()) + list(articleTwo.tfMap.keys())
        groupTfMap = set(groupTfMap)
        docProductNumber = 0
        euclideanLenOfOne = 0
        euclideanLenOfTwo = 0
        for term in groupTfMap:
            tfidfOne = articleOne.tfMap[term]['tfidf'] if term in articleOne.tfMap.keys() else 0
            tfidfTwo = articleTwo.tfMap[term]['tfidf'] if term in articleTwo.tfMap.keys() else 0

            docProductNumber += tfidfOne * tfidfTwo
            euclideanLenOfOne += pow(tfidfOne, 2)
            euclideanLenOfTwo += pow(tfidfTwo, 2)
        similarity = docProductNumber / (1 + sqrt(euclideanLenOfOne) * sqrt(euclideanLenOfTwo))
        return similarity

    def getClustersOfKMeans(self, newsNodes, kValue):
        if newsNodes.__len__() < kValue:
            raise Exception('k is must smaller than count of nodes')
        clusterList = []
        for news in newsNodes[0:kValue]:
            centroid = news
            clusterList.append({'centroid': centroid, 'elementList': []})

        for idx in range(10):
            clusterList = self.applyClusterInKMeans(newsNodes, clusterList)
            for element in clusterList[0]['elementList']:
                print(element.article)
            print('--------------')
            for cluster in clusterList:
                cluster['centroid'] = self.makeCentroid(cluster)
                cluster['elementList'] = []
        return clusterList


    def applyClusterInKMeans(self,newsNodes,preClusterList):
        clusterList = preClusterList
        for news in newsNodes:
            selectedListIdx = -1
            highestSimilarity = 0
            for idx, cluster in enumerate(clusterList):
                currentSim = self.getSimilarity(news, cluster['centroid'])
                if currentSim > highestSimilarity:
                    highestSimilarity = currentSim
                    selectedListIdx = idx
            clusterList[selectedListIdx]['elementList'].append(news)
        return clusterList
    def makeCentroid(self,cluster):
        # 그저 tfidf값을 재계산 안하고 있는 그대로 평균을 내도 괜찮을까?
        elementList = cluster['elementList']

        tfMap = {}
        lengthOfCluster = cluster.__len__()
        for listElement in elementList:
            for key, pureTfElement in listElement.tfMap.items():

                if key not in tfMap:
                    tfMap[key] = pureTfElement
                else:
                    tfElement = tfMap[key]
                    tfElement['count'] += pureTfElement['count']
                    tfElement['tf'] += pureTfElement['tf']
                    tfElement['tfidf'] += pureTfElement['tfidf']
        for key, tfElement in tfMap.items():
            tfElement['count'] /= lengthOfCluster
            tfElement['tf'] /= lengthOfCluster
            tfElement['tfidf'] /= lengthOfCluster
        newsNodeForCentroid = NewsNode()
        newsNodeForCentroid.tfMap = tfMap
        newsNodeForCentroid.countTerms = 0
        return newsNodeForCentroid




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
