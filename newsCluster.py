import hashlib

import sys
from konlpy.tag import Mecab
from math import log, sqrt


class NewsCluster:
    def __init__(self):
        self.trash = 0
        self.nlpWorker = Mecab()
        self.newsNodes = []

    def extractTfFromArticleList(self, articleList):
        for article in articleList:
            self.newsNodes.append(self.extractTf(article))

        return self.newsNodes

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
    def setIdfInNewsNode(self):
        for news in self.newsNodes:
            # print(news.tfMap)
            for term in news.tfMap.keys():
                news.tfMap[term]['idf'] = self.getIdfValue(term)
                news.tfMap[term]['tfidf'] = news.tfMap[term]['tf'] * news.tfMap[term]['idf']

    def getIdfValue(self, term):
        matchedCount = 0
        for news in self.newsNodes:
            if term in news.tfMap.keys():
                matchedCount += 1
        # @ Critical issue : 어떠한 상황에서 idf 값이 마이너스가 나옴. 수식에서 마이너스의 가능성을 찾아보고 그에 대한 방안을 마련할 필요가 있다
        return log(self.newsNodes.__len__() / (1 + matchedCount))

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



    def getClustersOfKMeansHandler(self):

        initialKValue = round(sqrt(self.newsNodes.__len__() / 2))
        # initialKValue = 35
        clusterList = []
        dunnIndex = 0
        kWeight = 0
        while True:
            anotherClusterList = self.getClustersOfKMeans(self.newsNodes,initialKValue+kWeight)
            anotherDunnIndex = self.evalDunnIndex(anotherClusterList)
            # if clusterList is not None and dunnIndex > anotherDunnIndex:
            #     return clusterList
            clusterList = anotherClusterList
            print('k: '+str(kWeight)+', '+str(anotherDunnIndex*1000000))
            dunnIndex = anotherDunnIndex
            kWeight += 1


    def getClustersOfKMeans(self, newsNodes, kValue):
        if newsNodes.__len__() < kValue:
            raise Exception('k is must smaller than count of nodes')
        clusterList = []
        for news in newsNodes[0:kValue]:
            centroid = news
            clusterList.append({'centroid': centroid, 'elementList': []})

        for idx in range(20):
            clusterList = self.applyClusterInKMeans(newsNodes, clusterList)
            anotherDunnIndex = self.evalDunnIndex(clusterList)
            print(str(anotherDunnIndex*1000000))
            # for element in clusterList[0]['elementList']:
                # print(element.simValue)
                # print(element.article)
            # print('--------------')
            # if idx == 9 :
            #     break
            for cluster in clusterList:
                cluster['centroid'] = self.makeCentroid(cluster)
                cluster['elementList'] = []

        return clusterList


    def evalDunnIndex(self,clusterList):
        dissimilarityVal = sys.maxsize
        for cluster in clusterList:
            for element in cluster['elementList']:
                for anotherElement in cluster['elementList']:
                    sim = self.getSimilarity(element, anotherElement)
                    if dissimilarityVal > sim:
                        dissimilarityVal = sim
        similarityOfCentroid = 0
        for cluster in clusterList:
            centroid = cluster['centroid']
            for anotherCluster in clusterList:
                if centroid != anotherCluster['centroid']:
                    sim = self.getSimilarity(centroid,anotherCluster['centroid'])
                    if sim > similarityOfCentroid:
                        similarityOfCentroid = sim
        # 멀수록 유사도가 0에 수렴하기 때문에 이를 역으로 취하기 위해 아래 과정을 취함
        disSimWeight = 1/dissimilarityVal
        simWeight = 1/similarityOfCentroid

        return simWeight / disSimWeight




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

            news.simValue = highestSimilarity
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

    def runOfKMeans(self, articleList):
        self.extractTfFromArticleList(articleList)
        self.setIdfInNewsNode()
        return self.getClustersOfKMeansHandler()


class NewsNode:
    def __init__(self):
        self.countTerms = 0
        self.article = ''
        self.tfMap = {}
        self.simValue = 0

    def __add__(self, element):
        if element in self.tfMap.keys():
            self.tfMap[element]['count'] = self.tfMap[element]['count'] + 1
        else:
            self.tfMap[element] = {'count': 1}
        self.countTerms += 1
