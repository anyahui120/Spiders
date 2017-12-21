#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Author  : Ann
# @Time    :

'''
    Attempt at auto-downloading the actual urls of videos and other materials from xuetangx.com
    TODO: Do proper argument handling and associated processing
    - specify e-mail, password
    - download available courses in you own account
    - map actual urls and resources, do not have to download all the resources themselves.
'''
#Usage
#command python futurelearn_crawler.py email password

import sys, os, errno
import requests
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
reload(sys)
sys.setdefaultencoding('utf-8')

# 建立浏览器对象 ，通过Phantomjs
browser = webdriver.PhantomJS('C:\\Users\\workshop\\Desktop\\phantomjs.exe')
# 设置访问的url
# SIGNIN_URL = 'https://www.open2study.com/login'
email = 'an6582807003@yeah.net'
password = 'kkJ-2vg-SeF-zrs'


DASHBOARD = 'http://www.xuetangx.com/dashboard/'

try:
    browser.get(DASHBOARD)
    # browser.save_screenshot('login.png')
    browser.maximize_window()
    browser.implicitly_wait(50)

    email_field = browser.find_element_by_name('username')
    password_field = browser.find_element_by_name("password")
    email_field.send_keys(email)
    password_field.send_keys(password)
    button = browser.find_element_by_id('loginSubmit')
    button.click()
except Exception,e:
    print e
    browser.quit()


courses_list = browser.find_element_by_class_name('course_info_list').find_elements_by_tag_name('li')
courses = dict()
for course in courses_list:
    course_href = course.find_element_by_tag_name('a').get_attribute('href')
    course_name = course.find_element_by_class_name('course_name').text
    print course_name, course_href
    courses[course_name] = course_href

for course_key in courses.keys():
    course_name = course_key
    course_href = courses[course_name]

    browser.get(course_href)
    browser.maximize_window()
    browser.save_screenshot('dashboard.png')
    blocks_tree = browser.find_element_by_id('accordion')
    chapter_list = blocks_tree.find_elements_by_class_name('chapter')
    for chapter in chapter_list:
        # 展开目标模块
        button = chapter.find_element_by_tag_name('h3')
        button.click()
        browser.save_screenshot('test.png')
        # Expand to see all Modules
        chapter_name = chapter.find_element_by_tag_name('h3').text
        chapter_topics = chapter.find_elements_by_tag_name('li')
        for topic in chapter_topics:
            topic_name = topic.find_element_by_tag_name('a').text
            topic_href = topic.find_element_by_tag_name('a').get_attribute('href')
            print course_name, topic_name, topic_href

browser.quit()

#结束
