from setuptools import setup


setup(
    name='cluster_the_article',
    version='0.0.1',
    description='',
    url='https://github.com/yoonsubKim/cluster-the-news.git',
    author='rupert kim',
    author_email='my@rupert.in',
    license='MIT',
    packages=[
        'cluster_the_article',
    ],
    install_requires=[
        'copy',
        'sys',
        'numpy',
        'Mecab',
        'sqrt',
        'log',
    ]
)