import re
import sys
from math import log, sqrt

from konlpy.tag import Mecab


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
        afterNLP = self.nlpWorker.pos(article)

        newsNode = NewsNode()
        newsNode.article = article
        for element in afterNLP:
            term = element[0]
            type = element[1]
            # 부호 삭제
            if bool(re.match('SF|SP|SS|SE|SO|SW|SY|SC',type)):
                continue
            if bool(re.match('J\D+',type)):
                continue
            if bool(re.match('E\D+',type)):
                continue
            if bool(re.match('X\D+',type)):
                continue
            if bool(re.match('NP\D*',type)):
                continue
            if bool(re.match('MAJ',type)):
                continue
            if type == 'VA':
                continue
            if type == 'VV' and type.__len__() == 1:
                continue
            if bool(re.search('ETM',type)):
                continue
            newsNode.__add__(element)


        self.calcTf(newsNode)

        return newsNode
    def calcTf(self,newsNode):
        for key in newsNode.tfMap.keys():
            newsNode.tfMap[key]['tf'] = 0.5 + 0.5 * newsNode.tfMap[key]['count'] / newsNode.countTerms
    # def extractIdf(self):
    def setIdfInNewsNode(self):
        termMap = {}
        for news in self.newsNodes:
            for term in news.tfMap.keys():
                if term not in termMap.keys():
                    termMap[term] = news.tfMap[term]['count']
                else:
                    termMap[term] += news.tfMap[term]['count']

        for news in self.newsNodes:
            # print(news.tfMap)
            for term in news.tfMap.keys():
                news.tfMap[term]['idf'] = self.getIdfValue(term,termMap)
                news.tfMap[term]['tfidf'] = news.tfMap[term]['tf'] * news.tfMap[term]['idf']

    def getIdfValue(self, term,termMap):
        matchedCount = termMap[term]
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

            type = articleOne.tfMap[term]['type'] if term in articleOne.tfMap.keys() else articleTwo.tfMap[term]['type']

            if type == 'NNP':
                docProductNumber += pow(tfidfOne,2) * pow(tfidfTwo,2)
            else:
                docProductNumber += tfidfOne * tfidfTwo

            euclideanLenOfOne += pow(tfidfOne, 2)
            euclideanLenOfTwo += pow(tfidfTwo, 2)
        similarity = docProductNumber / (1 + sqrt(euclideanLenOfOne) * sqrt(euclideanLenOfTwo))

        return similarity



    def getClustersOfKMeansHandler(self):

        initialKValue = round(sqrt(self.newsNodes.__len__() / 2))
        # initialKValue = 35
        clusterList = []
        RSSValue = 0
        kWeight = 0
        while True:
            anotherClusterList = self.getClustersOfKMeans(initialKValue+kWeight)
            anotherRSSValue = self.evalRSS(anotherClusterList)
            if anotherRSSValue / self.newsNodes.__len__()  < 0.3:
                return clusterList
            clusterList = anotherClusterList
            print('k: '+str(initialKValue+kWeight)+', '+str(anotherRSSValue))
            RSSValue = anotherRSSValue
            kWeight += 1


    def getClustersOfKMeans(self, kValue):
        if self.newsNodes.__len__() < kValue:
            raise Exception('k is must smaller than count of nodes')
        clusterList = self.getTopDownClusters(kValue)

        previousRSSValue = sys.maxsize
        while True:
            clusterList = self.applyClusterInKMeans(self.newsNodes, clusterList)
            anotherRSSValue = self.evalRSS(clusterList)
            # print(str(anotherRSSValue))
            # for element in clusterList[0]['elementList']:
                # print(element.simValue)
                # print(element.article)
            # print('--------------')
            if previousRSSValue == anotherRSSValue:
                break
            previousRSSValue = anotherRSSValue
            for cluster in clusterList:
                cluster['centroid'] = self.makeCentroid(cluster)
                cluster['elementList'] = []

        return clusterList

    def evalRSS(self,clusterList):
        rssOfAll = 0
        for cluster in clusterList:
            centroid = cluster['centroid']
            rssOfOneCluster = 0
            for element in cluster['elementList']:
                distanceWithCenter = 1 - element.simValue
                rssOfOneCluster += pow(distanceWithCenter,2)

            rssOfAll += rssOfOneCluster
        return rssOfAll


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
        idxList = self.getEmptyClusterIdxs(clusterList)
        if not idxList:
            return clusterList
        return self.getAdjustedClusterList(newsNodes,clusterList,idxList)

    def getAdjustedClusterList(self, newsNodes, clusterList, emptiedIdxList):
        lowestNewsList = []
        for idx in range(emptiedIdxList.__len__()):
            lowestSimilarNews = None
            tmpSim = 1
            for news in newsNodes:
                if news.simValue < tmpSim and news not in lowestNewsList:
                    tmpSim = news.simValue
                    lowestSimilarNews = news
            lowestNewsList.append(lowestSimilarNews)

        for news in lowestNewsList:
            for cluster in clusterList:
                elementListOfCluster = cluster['elementList']
                isEliminated = False
                for idx,elementNews in enumerate(elementListOfCluster):
                    if news is elementNews:
                        del elementListOfCluster[idx]
                        isEliminated = True
                        break
                if isEliminated:
                    break

        for idx in emptiedIdxList:
            oneOfLowest = lowestNewsList.pop()
            oneOfLowest.simValue = 1
            clusterList[idx] = {'centroid': oneOfLowest, 'elementList': [oneOfLowest]}

        return clusterList




    def getEmptyClusterIdxs(self,clusterList):
        idxList = []
        for idx, cluster in enumerate(clusterList):
            if not cluster['elementList']:
                idxList.append(idx)
        return idxList

    def makeCentroid(self,cluster):
        newsList = cluster['elementList']
        return self.makeCentroidWithNewsList(newsList)
    def makeCentroidWithNewsList(self,newsList):

        tfMap = {}
        allarticles = ""

        for listElement in newsList:
            allarticles += listElement.article
            for key, pureTfElement in listElement.tfMap.items():

                if key not in tfMap:
                    tfMap[key] = {}
                    tfElement = tfMap[key]
                    tfElement['count'] = pureTfElement['count']
                    tfElement['idf'] = pureTfElement['idf']
                    tfElement['type'] = pureTfElement['type']
                else:
                    tfElement = tfMap[key]
                    tfElement['count'] += pureTfElement['count']

        for key in tfMap.keys():
            tfMap[key]['count'] /= newsList.__len__()

        newsNodeForCentroid = NewsNode()
        newsNodeForCentroid.tfMap = tfMap
        newsNodeForCentroid.recalcCountTerms()
        self.calcTf(newsNodeForCentroid)
        for key in tfMap.keys():
            tfMap[key]['tfidf'] = tfMap[key]['tf'] * tfMap[key]['idf']

        newsNodeForCentroid.article = allarticles
        return newsNodeForCentroid

    def runOfKMeans(self, articleList,**kwargs):
        self.extractTfFromArticleList(articleList)
        self.setIdfInNewsNode()
        if kwargs.get('extraList',None) is not None:
            for idx,extra in enumerate(kwargs.get('extraList')):
                self.newsNodes[idx].extra = extra
        return self.getClustersOfKMeansHandler()
    def runOfHAC(self,articleList):
        self.extractTfFromArticleList(articleList)
        self.setIdfInNewsNode()
        return self.getClustersOfHAC(10)

    def getClustersOfHAC(self,kValue):
        if self.newsNodes.__len__() < kValue:
            raise Exception('k is must smaller than count of nodes')
        clusterList = []
        for idx, news in enumerate(self.newsNodes):
            centroid = news
            clusterList.append({'centroid': centroid, 'elementList': [], 'HId':idx})

        simList = []
        for idxX, clusterX in enumerate(clusterList):
            for idxY, clusterY in enumerate(clusterList):
                if idxX <= idxY:
                    break
                sim = self.getSimilarity(clusterX['centroid'],clusterY['centroid'])
                simList.append({'sim':sim,'x':clusterX,'y':clusterY})



        while clusterList.__len__() != kValue:

            simObject = max(simList, key=lambda item: item['sim'])
            simObjectX = simObject['x']['centroid']
            simObjectY = simObject['y']['centroid']

            simObjectX = self.makeCentroidWithNewsList([simObjectX, simObjectY])


            for idx,cluster in enumerate(clusterList):
                if cluster['HId'] == simObject['y']['HId']:
                    clusterList.remove(cluster)
                if cluster['HId'] == simObject['x']['HId']:
                    # cluster['centroid'].tfMap = {}
                    cluster['centroid'] = simObjectX


            for simLoop in simList:
                if simLoop['x'] == simObject['y'] or simLoop['y'] == simObject['y']:
                    simList.remove(simLoop)
                    continue
                if simLoop['x'] == simObject['x'] or simLoop['y'] == simObject['x']:
                    sim = self.getSimilarity(simObjectX , simObjectY)
                    simLoop['sim'] = sim


        return clusterList


    def getTopDownClusters(self,kValue):
        if self.newsNodes.__len__() < kValue:
            raise Exception('k is must smaller than count of nodes')
        clusterList = []
        clusterList.append({'centroid': self.newsNodes[0], 'elementList': []})
        while clusterList.__len__() != kValue:
            smallestSim = sys.maxsize
            smallestNode = None
            for node in self.newsNodes:
                sumOfSims = 0
                for idx, cluster in enumerate(clusterList):
                    sumOfSims += pow(self.getSimilarity(cluster['centroid'],node),2)
                if smallestSim > sumOfSims:
                    smallestSim = sumOfSims
                    smallestNode = node
            clusterList.append({'centroid': smallestNode, 'elementList': []})
        return clusterList


class NewsNode:
    def __init__(self):
        self.countTerms = 0
        self.article = ''
        self.tfMap = {}
        self.simValue = 0
        self.extra = {}

    def __add__(self, element):

        term = element[0]
        type = element[1]
        if term in self.tfMap.keys():
            self.tfMap[term]['count'] = self.tfMap[term]['count'] + 1
        else:
            self.tfMap[term] = {'count': 1, 'type': type}
        self.countTerms += 1
    def recalcCountTerms(self):
        self.countTerms = 0
        for key in self.tfMap.keys():
            self.countTerms += self.tfMap[key]['count']
