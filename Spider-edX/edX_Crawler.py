#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Author  : Ann
# @Time    :

'''
    Attempt at auto-downloading the actual urls of videos and other materials from edx.com
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


DASHBOARD = 'https://courses.edx.org/dashboard'

try:
    browser.get(DASHBOARD)
    # browser.save_screenshot('login.png')
    browser.maximize_window()
    browser.implicitly_wait(100)

    email_field = browser.find_element_by_id('login-email')
    password_field = browser.find_element_by_id("login-password")
    email_field.send_keys(email)
    password_field.send_keys(password)
    button = browser.find_element_by_class_name('login-button')
    button.click()
    browser.implicitly_wait(100)
except Exception,e:
    print e
    browser.quit()
# browser.save_screenshot('dashboard.png')

courses_list = browser.find_elements_by_class_name('course-title')
courses = dict()
for course in courses_list:
    course_href = course.find_element_by_tag_name('a').get_attribute('href')
    course_name = course.find_element_by_tag_name('a').text
    print course_name, course_href
    courses[course_name] = course_href

for course_key in courses.keys():
    course_name = course_key
    course_href = courses[course_name]
    browser.get(course_href)
    browser.implicitly_wait(10)
    browser.maximize_window()
    blocks_tree = browser.find_element_by_class_name('block-tree')
    episodes_list = blocks_tree.find_elements_by_css_selector('.outline-item.focusable.section')
    for episode in episodes_list:
        episode_name = episode.find_element_by_class_name('section-title').text
        episode_topics = episode.find_elements_by_tag_name('li')
        for topic in episode_topics:
            topic_name = topic.find_element_by_tag_name('a').text
            topic_href = topic.find_element_by_tag_name('a').get_attribute('href')
            print course_name, topic_name, topic_href

browser.quit()

#结束
