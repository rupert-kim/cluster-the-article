## Cluster The Article

This is the cluster program which can separate a lot of articles with K-means Algorithm and especially optimized to Korean Articles.
Contact to me (my@rupert.in) if you want to tell any problems you have or give me a nice idea.


## requirements

It is essential to install Mecab Library on your machine what you want to run.
Please check KoNLP WebSite(http://konlpy-ko.readthedocs.io/ko/v0.4.3/install/)

## How to import
You can import with the __pip command line__
 ```
 pip install git+https://github.com/yoonsubKim/cluster-the-article.git
```

## How to use

Recommend referring the example programs which is in the example directory.
To classify the articles, the __runOfKmeans__ method response the cluster data, and this is one of the major functions. In addition, if you want to try to use other methods in this library. there will be no trouble.
```
clusterManager = ArticleCluster()
clusterList = clusterManager.runOfKMeans(articleList)

```