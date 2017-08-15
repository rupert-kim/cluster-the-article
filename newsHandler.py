

from daumNewsParser import DaumNewsParse
from newsCluster import NewsCluster,NewsNode

parser = DaumNewsParse()
clusterManager = NewsCluster()
aa = NewsNode()
newsNodes = []
for urlObject in parser.parseUrlList(paramDate='20050101'):
    article = parser.parseArticle(url=urlObject['href'])

    newsNodes.append(clusterManager.extractTf(article))

for news in newsNodes:
    for term in news.tfMap.keys():
        news.tfMap[term]['idf'] = clusterManager.getIdfValue(newsNodes,term)
        news.tfMap[term]['tfidf'] = news.tfMap[term]['tf'] * news.tfMap[term]['idf']

maxSimilarity = 0
maxGroup = []
for news in newsNodes:
    for compareNews in newsNodes:
        if news is not compareNews:
            similarity = clusterManager.getSimilarity(news,compareNews)
            if similarity > maxSimilarity:
                maxSimilarity = similarity
                maxGroup.append([news,compareNews])

