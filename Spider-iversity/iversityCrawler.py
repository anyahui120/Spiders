#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Author  : Ann
# @Time    :

'''
    Attempt at auto-downloading the actual urls of videos and other materials from open2study.com
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


# Crawl the dashboard for all the current courses.
DASHBOARD = 'https://iversity.org/en/my/courses'

try:
    browser.get(DASHBOARD)
    # browser.save_screenshot('login.png')
    browser.maximize_window()
    browser.implicitly_wait(50)
    #找到登录按钮
    login_button = browser.find_element_by_xpath('//*[@id="login-link"]')
    login_button.click()
    browser.save_screenshot('test.png')
    #登录窗口为悬浮窗口，需要使用switch_to_alert函数
    browser.switch_to_alert()
    browser.save_screenshot('test.png')
    #剩下的步骤与其他爬虫程序相同

    email_field = browser.find_element_by_id("session_email0")
    password_field = browser.find_element_by_id("session_password0")
    email_field.send_keys(email)
    password_field.send_keys(password)
    browser.save_screenshot('test.png')
    button = browser.find_element_by_css_selector('.btn.btn-primary.graphic-chevron-right.btn-icon.d-block.btn-ajax')
    button.click()
    browser.save_screenshot('test.png')
    browser.implicitly_wait(50)
except Exception,e:
    print e
    browser.quit()
# browser.save_screenshot('dashboard.png')
# courses_anchor = browser.find_element_by_class_name('courses-list')
courses_anchor = browser.find_element_by_css_selector('#main > div > div > div > div:nth-child(2)')
courses_list = courses_anchor.find_elements_by_css_selector('.col-xs-6.col-sm-4.CourseCardsGrid__Column')
course_name_url = dict()
for eachCourse in courses_list:
    # browser.save_screenshot('test.png')
    course_name = eachCourse.find_element_by_tag_name('h3').text
    course_href = eachCourse.find_element_by_tag_name('a').get_attribute('href')
    course_name_url[course_name] = course_href

course_module_topics = dict()
for key in course_name_url.keys():
    courseName = key
    course_classroom_URL = course_name_url[key] + '/lesson_units'

    browser.get(course_classroom_URL)
    browser.maximize_window()
    browser.implicitly_wait(50)


    chapters_list = browser.find_elements_by_css_selector('.chapter-units-wrapper.clearfix.js-chapter-units-wrapper')

    for chapter in chapters_list:
        chapter_name = chapter.find_element_by_class_name('chapter-title').text
        chapter_button = chapter.find_element_by_tag_name('i').click()
        browser.implicitly_wait(5)
        topics = chapter.find_elements_by_tag_name('li')
        for topic in topics:
            topic_href = topic.find_element_by_tag_name('a').get_attribute('href')
            topic_name = topic.find_element_by_class_name('unit-title').text
            print courseName, chapter_name, topic_name, topic_href

browser.quit()

#结束



