

from daumNewsParser import DaumNewsParse
from newsCluster import NewsCluster

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

clusterManager.runOfKMeans(articleList)


print('-----')
