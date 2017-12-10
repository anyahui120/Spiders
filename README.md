# Spiders
This project contains spiders for coursera, edx, open2study, xuetangx, futurelearn and icourses.
The Spiders are used to crawl the actual urls of resources in these platforms and corresponding basic informations of a course.

Requirements are differnt for each Spider.

[1] Coursera

[2] edx

    1. Python 2.7
    2. Scrapy

[3] open2study

[4] xuetangx

[5] futurelearn

    1. Python 2.7

    2. bs4(BeautifulSoup)

[6] icourses

Usage:

[1] Coursera

[2] edx

    1. Change the path to .py you want to run in the command line 
    
    2. scrapy crawl edx -o ./data/items.json

[3] open2study

[4] xuetangx

[5] futurelearn

    1. Change the path to the path of .py you want to run.
    
    2. python futurelearn_crawler.py email password

[6] icourses

