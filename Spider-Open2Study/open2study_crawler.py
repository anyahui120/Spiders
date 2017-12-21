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
DASHBOARD = 'https://www.open2study.com/dashboard'

try:
    browser.get(DASHBOARD)
    # browser.save_screenshot('login.png')
    browser.maximize_window()
    browser.implicitly_wait(5)

    email_field = browser.find_element_by_id("login-username")
    password_field = browser.find_element_by_id("login-password")
    email_field.send_keys(email)
    password_field.send_keys(password)
    button = browser.find_element_by_id('login-submit')
    button.submit()
    browser.implicitly_wait(10)
except Exception,e:
    print e
    browser.quit()
# browser.save_screenshot('dashboard.png')
completed_courses_page = browser.find_element_by_id('completed_courses_tab')
completed_course_href = completed_courses_page.find_element_by_tag_name('a').get_attribute('href')
browser.get(completed_course_href)
browser.implicitly_wait(10)

#one problem:怎样控制页面显示完全？？？这是一个大问题，程序的不稳定性主要体现在这里。
courses_list = browser.find_elements_by_class_name('oua-completed-courses-block-content')
course_name_url = dict()
for eachCourse in courses_list:
    # browser.save_screenshot('test.png')
    courseURL = eachCourse.find_element_by_class_name('dashboard_current_course_title').find_element_by_tag_name('a').get_attribute('href')
    courseName = eachCourse.find_element_by_class_name('dashboard_current_course_title').text.split('\n')[0]

    classroomURL = eachCourse.find_element_by_class_name('gotoclassroom').find_element_by_tag_name(
        'a').get_attribute('href')
    # print courseName, courseURL, classroomURL
    course_name_url[courseName] = [courseURL,classroomURL]

# Crawl resources for every course
course_module_topics = dict()
for key in course_name_url.keys():
    courseName = key
    print courseName
    course_classroom_URL = course_name_url[key][1]
    browser.get(course_classroom_URL)
    browser.maximize_window()
    browser.implicitly_wait(5)
    modules_div = browser.find_element_by_class_name('jspPane')
    modules_ul = modules_div.find_element_by_tag_name('ul')
    module_topics = dict()
    try:
        modules_1 = modules_ul.find_elements_by_css_selector('.module.open')
        for module in modules_1:
            try:
                module_name = module.find_element_by_class_name('module').text
                module_topics = module.find_elements_by_tag_name('li')

                #展开目标模块
                button = module.find_element_by_class_name('name')
                button.click()
                browser.save_screenshot('test.png')
                #Expand to see all Modules
                button = browser.find_element_by_css_selector('.resize.collapsed')
                button.click()
                browser.save_screenshot('test.png')

                topics = []
                for topic in module_topics:
                    topic_href = topic.find_element_by_tag_name('a').get_attribute('href')
                    topic_name = topic.find_element_by_class_name('topicname').text
                    topics.append([topic_name, topic_href])
                    print courseName, course_name_url[key][0], module_name, topic_name, topic_href
                module_topics[module_name] = topics
            except Exception,e:
                print "This is not a module, continuing..."
                continue
    except Exception,e:
        print e
        pass
    try:
        modules_2 = modules_ul.find_elements_by_css_selector('.module.closed')
        for module in modules_2:
            browser.save_screenshot('test.png')
            try:
                module_name = module.find_element_by_class_name('module').text
                module_topics = module.find_elements_by_tag_name('li')

                #展开目标模块
                button = module.find_element_by_class_name('name')
                button.click()
                browser.save_screenshot('test.png')
                #Expand to see all Modules
                button = browser.find_element_by_css_selector('.resize.collapsed')
                button.click()
                browser.save_screenshot('test.png')

                topics = []
                for topic in module_topics:
                    topic_href = topic.find_element_by_tag_name('a').get_attribute('href')
                    topic_name = topic.find_element_by_class_name('topicname').text
                    topics.append([topic_name, topic_href])
                    print courseName, course_name_url[key][0], module_name, topic_name, topic_href
                module_topics[module_name] = topics
            except Exception,e:
                print "This is not a module, continuing..."
                continue
    except Exception, e:
        print e
        pass

    course_module_topics[courseName] = [course_name_url[key][0],module_topics]
#test
browser.quit()

#结束
