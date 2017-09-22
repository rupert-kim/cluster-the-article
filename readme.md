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

![](https://github.com/yoonsubKim/cluster-the-article/blob/master/example/article%20network%20example.gif?raw=true)


## Work Flow of the algorithm
1. Making vector value
> + To measure similarity between articles, makes term group of all articles through morpheme analyzer and extract vector value of each term with TF-IDF
2. Deciding K value of K-Means and centroids
> + For starting from the enough number of cluster, K is started from √(n/2)
> + To take an efficient result, the article that is the furthest one from other centroids is selected, and it is set to the centroid of the new cluster; this is following the rule of the top down clustering of the Hierarchical Cluster policy.
> + The distance of similarity of between a couple of articles is measured with Cosine Similarity
3. Making clusters
> + through the Cosine Similarity, all articles are linked to centroids that are made in pre-step
4. Adjusting the position of centroids
> + After clustering the articles, every cluster makes centroid move with the vector value of TF, and keep repeating this process until all nodes don’t move.
5. Repeat or response the clusters
> + the RSS value(Residual Sum of Squares) is measured and compared with pre-process what the value is decreased enough. the value is fixed to 0.4. If the value doesn't satisfy the criteria, the process is repeated with grown K + 1 value.

## other things
+ If you want to check the program that I made with this Library. Check out this
```
https://github.com/yoonsubKim/cluster-the-news-webapp
```