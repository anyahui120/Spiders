#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Author  : Ann
# @Time    :

'''
    Attempt at auto-downloading the actual urls of videos and other materials from futurelearn.com
    TODO: Do proper argument handling and associated processing
    - specify e-mail, password
    - download available courses in you own account
    - map actual urls and resources, do not have to download all the resources themselves.
'''
#Usage
#command python futurelearn_crawler.py email password

import sys, os, errno
import requests
import json
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

SIGNIN_URL = 'https://www.futurelearn.com/sign-in'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36',
    'content-type': 'application/json',
}
## -- Functions: ---------------------------------------------------

def getToken(session, url):
    ''' Perform request to the specified signin url and extract the 'authenticity_token'
        RETURN: token and cookies
    '''
    response = session.get(url, headers=headers)
    # showResponse(response)
    content = response.content.decode('utf8')
    apos = content.find("authenticity_token")
    vpos = content[apos:].find("value=")
    token_pos = apos + vpos + len("value=") + 1
    close_quote_pos = token_pos + content[token_pos:].find('"')
    token = content[token_pos: close_quote_pos]

    return token, response.cookies


def login(session, url, email, password, token, cookies):
    ''' Perform request to the specified signin url to perform site login
        RETURN: response
    '''
    data = json.dumps({'email': email, 'password': password, 'authenticity_token': token})

    response = session.post(url, headers=headers, cookies=cookies, data=data)
    content = response.content.decode('utf8')

    return response


def get_all_courses_homepage(URL_after_login):
    '''
    Get all the courses the target user enrolled.
    :param URL_after_login: the redirect url when login
    :return: {course_name_slug:course_url}
    {course_name_slug:weeks_list}
    '''
    course_in_progress_list = dict()
    course_weeks = dict()
    response = session.get(URL_after_login, headers = headers)
    content = response.content.decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    your_courses = soup.findAll('a', {'class': "title"})
    for course in your_courses:
        course_name_slug = course['href'].split('/')[2]
        course_name = course['title']
        course_url = 'https://www.futurelearn.com' + course['href']
        course_in_progress_list[course_name_slug] = course_url
        #find the weeks id for each course
        temp = soup.find_all('div',{'aria-label':course_name})
        if len(temp) != 0:
            temp = temp[0]
            week_list = []

            weeks = temp.findAll('a')
            for week in weeks:
                week_url = 'https://www.futurelearn.com' + week['href']
                week_list.append(week_url)
                course_weeks[course_name_slug] = week_list
        else:
            continue
    return course_in_progress_list, course_weeks

def get_course_weeks(course_week):
    '''
    :param course_week: the week number for each week of a course
    :return: resource data structure
    '''
    resource = []
    response = session.get(course_week, headers = headers)
    content = response.content.decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    list_sections = soup.findAll('li',{'class': ['list-nestedgroup', 'activity', 'u-clearfix']})
    for section in list_sections:
        subsections = section.findAll('li')
        for subsection in subsections:
            temp = subsection.findAll('a',{'class': ['m-composite-link', 'm-composite-link--with-step', 'm-composite-link--wrapped']})
            if len(temp) != 0:
                resource_url =  'https://www.futurelearn.com' + temp[0]['href']
                resource_identifier = subsection.findAll('span', {'class': 'm-composite-link__identifier'})[0].next.contents[0]
                resource_name = subsection.findAll('span', {'class': 'm-composite-link__primary'})[0].contents[0]
                resource_type = subsection.findAll('span', {'class': 'm-composite-link__secondary type'})[0].contents[0]
                print "Downloading %s" % str(resource_identifier)
                resource.append([resource_url, resource_identifier, resource_type, resource_name])
    return resource

## -- Main: --------------------------------------------------------
# email = sys.argv[1]
# password = sys.argv[2]
email = '1316025850@qq.com'
password = 'anyahui120'
URL_after_login = 'https://www.futurelearn.com/your-courses/in-progress'
session = requests.Session()


## -- do the login:
token, cookies = getToken(session, SIGNIN_URL)
response = login(session, SIGNIN_URL, email, password, token, cookies)
course_in_progress_list, course_weeks = get_all_courses_homepage(URL_after_login)
course_resources = dict()
for key,value in course_weeks.items():
    course_name_slug = key
    course_weeks_list = value
    print course_name_slug
    resources = []
    if len(course_weeks_list) == 0:
        print "%s is not available for free now. Please upgrade if you want to get the resources." % course_name_slug
    else:
        for week in course_weeks_list:
            resource_list= get_course_weeks(week)
            resources.append(resource_list)
        course_resources[course_name_slug] = resources

print "Finished crawling all the available courses in your account!"

