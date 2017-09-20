from datetime import datetime

from articleCluster import NewsCluster
from example.daumNewsParser import DaumNewsParse

parser = DaumNewsParse()
clusterManager = NewsCluster()
newsNodes = []
articleList = []
urlList = parser.parseUrlList(paramDate='20160115')
print(urlList.__len__())
number = 0
for urlObject in urlList:
    number+=1
    print(number)
    article = parser.parseArticle(url=urlObject['href'])
    if article is not None:
        articleList.append(article)


clusterList = clusterManager.runOfKMeans(articleList)

# clusterManager.runOfHAC(articleList)


