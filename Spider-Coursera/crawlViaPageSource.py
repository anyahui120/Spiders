#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
@author: Ann
'''

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import html.parser
from bs4 import BeautifulSoup
import yaml
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class PageAnalyser:
    def __init__(self):
        with open('config.yml') as f:
            config = yaml.load(f)
        self.driver = webdriver.PhantomJS('C:/Users/workshop/Downloads/phantomjs-2.1.1-windows (1)/phantomjs-2.1.1-windows/bin/phantomjs.exe',
                                          service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.email = config['UserName']
        self.password = config['Password']
        self.courses = []

    def login(self):
        self.driver.get('https://www.coursera.org/?authMode=login')
        self.driver.set_window_size(2000, 1500)
        self.driver.implicitly_wait(20)
        email_field = self.driver.find_element_by_name("email")
        password_field = self.driver.find_element_by_name("password")
        email_field.send_keys(self.email)
        password_field.send_keys(self.password)
        password_field.submit()

    def source_page_content(self, courseName):
        """
        :param
            courseName: String format. The target course's name. To construct the start URL for crawling.
        :return:
            soup: page content.(String format)
        """
        site = "https://www.coursera.org/learn/" + courseName + "/home/welcome"
        # print site
        first_step = self.driver.get(site)
        self.driver.implicitly_wait(15)
        # element = WebDriverWait(self.driver, 100).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, ['rc-HomeLayoutBody', 'with-catalog-banner'])))
        html = self.driver.page_source
        html = str(html)
        # print html
        soup = BeautifulSoup(html, 'html.parser')
        return soup


    def get_session_start_time(self, soup):
        """

        :param
            soup: page content, returned by source_page_content()
        :return:
            session_start_time
        """

        mydivs = soup.findAll('div', { "class" : 'start-week-section' })
        session_start_time = ''
        for div in mydivs:
            if div['class'] == 'label':
                session_start_time_string = div.string
                session_start_time = session_start_time_string.split(' ')[-1]
        return session_start_time

    def get_instructor_university(self,soup):
        """

        :param
            soup: page content
        :return:
            course_standard_name: Accounting Analytics, String format
            course_university_name: University of Pennsylvania, String format
            course_instructor_name: Brian J Bushee & Christopher D. Ittner, String format

        """
        mydiv = soup.findAll('div', {'class' : ['rc-CourseNameHeader', 'vertical-box', 'align-items-absolute-center', 'styleguide']})
        course_standard_name = mydiv[0].findAll('h1')[0].string
        course_university_name_str = mydiv[0].findAll('h2')[0].span.span.string
        course_university_name = course_university_name_str
        mydivs = soup.findAll('div', {'class': 'instructor-image-container'})
        instructors = []
        for div in mydivs:
            inst_name = div.span.span.string
            instructors.append(inst_name)

        # what if this course has 1, 2, 3 or more instructors, how to combine instructors name.
        inst_name_str = instructors[0]
        for i in xrange(1, len(instructors)-1):
            inst_name_str +=  ',' + instructors[i]
        course_instructor_name = inst_name_str + '&' + instructors[len(instructors)-1]

        return course_standard_name, course_university_name, course_instructor_name

    def get_all_resource_info(self, soup):
        """
        Get all the resource information including resource type, resource relative location, resource name, resource actual URL
        :param
            soup: page content
        :return:
            (resource-name-text, resource-name-num, resource-type, resource-relative-location, resource-actual-URL)
            And save all these data into database.

        """
        courseVideo = []
        courseSupplement = []

        try:
            contents = soup.findAll('ul')
            content = contents[len(contents)-1]
            if content.attrs == {'class': ['rc-HomeWeekCards', 'nostyle']}:
                links = content.findAll('a')
                hrefs = []
                for link in links:
                    if link.attrs['class'] == ['rc-UngradedItemProgress', 'horizontal-box', 'align-items-vertical-center']:
                        hrefs.append(link.attrs['href'])
                prefix = 'https://www.coursera.org'
                for j in xrange(len(hrefs)):
                    href = hrefs[j]
                    href_split = href.split('/')
                    if 'lecture' in href_split:
                        source_url = prefix + href
                        self.driver.get(source_url)
                        time.sleep(5)
                        html_step2 = self.driver.page_source
                        html_step2 = str(html_step2)
                        soup = BeautifulSoup(html_step2, 'html.parser')
                        linkss = soup.findAll('ul')
                        for link in linkss:
                            if link.attrs['class'] == ['rc-LessonItems', 'nostyle']:
                                urls = link.findAll('a')
                                hrefs_step2 = []
                                for url in urls:
                                    if url.attrs['class'] == ['rc-ItemLink', 'nostyle']:
                                        hrefs_step2.append(url.attrs['href'])
                                for k in xrange(len(hrefs_step2)):
                                    href_step2 = hrefs_step2[k]
                                    temp = href_step2.split('/')
                                    source_name = temp[len(temp) - 1]
                                    source_id = temp[len(temp) - 2]
                                    source_type = temp[len(temp)-3]
                                    coursename = temp[len(temp) -4]
                                    courseVideo.append([coursename,source_type,source_id,source_name,href_step2])
                            else:
                                continue
                    elif 'supplement' in href_split:
                        courseSupplement.append([href_split[len(href_split)-4],href_split[len(href_split)-3], href_split[len(href_split)-2], href_split[len(href_split)-1],href])
                    elif 'quiz' in href_split:
                        courseSupplement.append([href_split[len(href_split) - 4], href_split[len(href_split) - 3],
                                                 href_split[len(href_split) - 2], href_split[len(href_split) - 1],
                                                 href])
                    elif 'discussionPrompt' or 'peer' or 'ungradedLti' in href_split:
                        courseSupplement.append([href_split[len(href_split) - 4], href_split[len(href_split) - 3],
                                                 href_split[len(href_split) - 2], href_split[len(href_split) - 1],
                                                 href])
                    else:
                        print href
                        print 'Not a lecture or supplement resource.'
                        self.driver.back()
            return courseVideo,courseSupplement
        except Exception,e:
            print e
            return 0

#
if __name__ == '__main__':
    pageAnalysis = PageAnalyser()
    pageAnalysis.driver.implicitly_wait(20)
    # pageAnalysis.login()
    # print 'Login Success!'

    soup_content = pageAnalysis.source_page_content('accounting-analytics')
    session_start_time = pageAnalysis.get_session_start_time(soup_content)
    print session_start_time
    course_standard_name, course_university_name, course_instructor_name = pageAnalysis.get_instructor_university(soup_content)
    print session_start_time


# if __name__ == '__main__':
#     pageAnalysis = pageAnalysiser()
#     pageAnalysis.driver.implicitly_wait(10)
#     pageAnalysis.login()
#     time.sleep(3)
#
#     with open('config.yml') as f:
#         config = yaml.load(f)
#     userId = config['UserId']
#     filePath = config['filePath']
#     conn = sqlite3.connect('/Users/anyahui/Downloads/lib4moocdata-master/coursera/data/nusdata.db')
#     c = conn.cursor()
#     courseNames = c.execute('select distinct(coursename) from forum').fetchall()
#     conn.commit()
#     conn.close()
#
#     conn = sqlite3.connect('/Users/anyahui/Documents/国外工作/MOOCWikification/courseVideo.db')
#     c = conn.cursor()
#     c.execute('drop table if exists courseVideo')
#     c.execute('''CREATE TABLE courseVideo ( \
#     coursename text, \
#     sourcetype text, \
#     sourceid text, \
#     sourcename text, \
#     sourceurl text, \
#     primary key(sourcename,sourceid))
#     ''')
#
#     for ii in xrange(len(courseNames)-145):
#         try:
#             course = courseNames[ii]
#             print 'Processing: %d/%d....'%(ii+1,len(courseNames))
#             courseName = course[0]
#             print courseName
#             courses,coursesupp = pageAnalysis.analyse(courseName)
#             for iii in xrange(len(courses)):
#                 courseVideo = courses[iii]
#                 coursen, source_type, source_id, source_name, source_url = courseVideo[0], courseVideo[1], courseVideo[2], \
#                                                                        courseVideo[3], courseVideo[4]
#                 # sourcenum_list = source_name.split('-')
#                 # if sourcenum_list[-1].isdigital() == True:
#                 #     if sourcenum_list[-2].isdigital() == True:
#                 #         sourcenum = ''.join([sourcenum_list[-2],'.',[sourcenum_list[-1]]])
#                 #     else:
#                 #         sourcenum = sourcenum_list[-1]
#                 # else:
#                 #     sourcenum = 0
#
#                 c.execute('insert OR IGNORE into courseVideo values(?,?,?,?,?)',
#                       (coursen, source_type, source_id, source_name, source_url,))
#             for jjj in xrange(len(coursesupp)):
#                 courseSPP = coursesupp[jjj]
#                 coursen, source_type, source_id, source_name, source_url = courseSPP[0], courseSPP[1], courseSPP[2], \
#                                                                        courseSPP[3], courseSPP[4]
#                 c.execute('insert OR IGNORE into courseVideo values(?,?,?,?,?)',
#                       (coursen, source_type, source_id, source_name, source_url,))
#
#         except Exception,e:
#             print e
#             continue
#         finally:
#             print "Finished!"
#     conn.commit()
#     conn.close()
#     pageAnalysis.driver.quit()
# # courseVideo.objects.all()

