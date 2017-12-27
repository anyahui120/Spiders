#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Time    : 7/17/2017 4:46 PM
# @Author  : Ann
# @Site    : 
# @File    :
# @Software: PyCharm

from selenium import webdriver
import sqlite3
import json
import pycurl
import StringIO
import certifi
import yaml
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# The enter web page: https://www.coursera.org/learn/accounting-analytics/home/welcome
# For session information and courseIds
# https://www.coursera.org/api/onDemandSessionMemberships.v1?q=byUser&userId=105956&fields=onDemandCourseMaterials.v2(moduleIds,modules,lessons,items,passableItemGroups,passableItemGroupChoices,passableLessonElements),onDemandCourseMaterialLessons.v1(elementIds),sessions&includes=onDemandCourseMaterials.v2(modules,lessons,items,passableItemGroups,passableItemGroupChoices,passableLessonElements),sessions
# paras: userId
# Returns: (courseId, endedAt, startedAt)

# For instructor information
# https://www.coursera.org/api/onDemandInstructorNotes.v1/?courseId=rc5KG0aUEeWG1w6arGoEIQ&includes=instructorIds&fields=instructors.v1(fullName)&q=byCourse
# paras: (courseId)
# returns: (department, firstname, fullname, lastname)

# For video, slides and excel-files
# https://www.coursera.org/api/onDemandCourseMaterials.v2?q=learner&learnerId=105956&courseId=rc5KG0aUEeWG1w6arGoEIQ&showLockedItems=true&fields=onDemandGuidedItemsProgress.v1(progressStates),onDemandGuidedNextSteps.v1(nextStep),moduleIds,modules,lessons,items,onDemandSessionMemberships.v1(sessions),onDemandCourseSchedules.v1(defaultSchedule),onDemandCourseMaterialLessons.v1(elementIds),onDemandCourseMaterialItems.v2(contentSummary,lockedStatus,itemLockedReasonCode)&includes=modules,lessons,items,onDemandSessionMemberships.v1(sessions)
# paras: (userId, courseId)
# returns: (module, lesson, [video, slide, excel-file])


class PageAnalyser:

    def __init__(self):
        with open('config.yml') as f:
            config = yaml.load(f)
        self.driver = webdriver.PhantomJS(config['phantomjsPath'])
        # self.driver.maximize_window()
        # self.driver.implicitly_wait(100)
        self.email = config['UserName']
        self.password = config['Password']
        self.courses = []

    def login(self):
        #to set_window_size
        self.driver.set_window_size(1124, 850)
        self.driver.get('https://www.coursera.org/?authMode=login')
        self.driver.implicitly_wait(100)
        self.driver.save_screenshot('test.png')
        email_field = self.driver.find_element_by_name("email")
        password_field = self.driver.find_element_by_name("password")
        email_field.send_keys(self.email)
        password_field.send_keys(self.password)
        time.sleep(10)
        login_field = self.driver.find_element_by_css_selector('.Button_1fxeab1-o_O-primary_cv02ee-o_O-md_28awn8.w-100')
        login_field.click()
        time.sleep(10)
        # password_field.submit()

    def get_cookie(self,CourseName):
        new_url = 'https://www.coursera.org/learn/%s/home/welcome' %CourseName
        # course_discussion_urls.append(new_url)
        self.driver.get(new_url)
        # get current cookie and save as file
        cookie_items = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        cookie = ';'.join(item for item in cookie_items)
        return cookie

    def get_courseIds(self, userId,cookie):
        course_api = 'https://www.coursera.org/api/openCourseMemberships.v1/?q=findByUser&userId=%s'%userId
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, course_api)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)

        courseIds = []
        if code == 200:
            json_data = b.getvalue()
            elements = json.loads(json_data)['elements']
            for e in elements:
                courseId = elements[e]['courseId']
                courseIds.append(courseId)
        return courseIds

    def get_session_membership(self, userId, cookie):
        session_api = 'https://www.coursera.org/api/onDemandSessionMemberships.v1?q=byUser&userId=%s&fields=onDemandCourseMaterials.v2(moduleIds,modules,lessons,items,passableItemGroups,passableItemGroupChoices,passableLessonElements),onDemandCourseMaterialLessons.v1(elementIds),sessions&includes=onDemandCourseMaterials.v2(modules,lessons,items,passableItemGroups,passableItemGroupChoices,passableLessonElements),sessions' % userId

        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, session_api)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)

        courseId_start_end = {}
        if code == 200:
            json_data = b.getvalue()
            sessions = json.loads(json_data)['linked']['onDemandSessions.v1']
            for link in range(len(sessions)):
                courseId = sessions[link]['courseId']
                endedAt = sessions[link]['endedAt']
                startedAt = sessions[link]['startedAt']
                courseId_start_end[courseId] = [startedAt, endedAt]
            print "Successfully get session information"
        else:
            print "Failed to get session information"
        return courseId_start_end

    def get_session_membership_by_courseId(self, userId, cookie, courseId):
        '''

        :param userId:
        :param cookie:
        :param courseId:
        :return:
        '''
        session_api = 'https://www.coursera.org/api/onDemandSessionMemberships.v1?q=activeByUserAndCourse&userId=%s&courseId=%s&fields=onDemandGuidedItemsProgress.v1(progressStates),onDemandGuidedNextSteps.v1(nextStep),onDemandCourseMaterials.v2(moduleIds,modules,lessons,items),sessions,onDemandCourseSchedules.v1(defaultSchedule),onDemandCourseMaterialLessons.v1(elementIds),onDemandCourseMaterialItems.v2(contentSummary,lockedStatus,itemLockedReasonCode)&includes=onDemandCourseMaterials.v2(modules,lessons,items),sessions'%(userId, courseId)
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, session_api)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)

        courseId_start_end = {}
        if code == 200:
            json_data = b.getvalue()
            sessions = json.loads(json_data)['linked']['onDemandSessions.v1']
            for link in range(len(sessions)):
                courseId = sessions[link]['courseId']
                endedAt = sessions[link]['endedAt']
                startedAt = sessions[link]['startedAt']
                courseId_start_end[courseId] = [startedAt, endedAt]
            print "Successfully get session information"
        else:
            print "Failed to get session information"
        return courseId_start_end

    def get_instructors(self, courseId, cookie):
        '''
        :param courseId:
        :param cookie:
        :return:
        '''
        inst_api = 'https://www.coursera.org/api/onDemandInstructorNotes.v1/?courseId=%s&includes=instructorIds&fields=instructors.v1(fullName)&q=byCourse' % courseId
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, inst_api)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)

        courseId_instructor = {}

        if code == 200:
            json_data = b.getvalue()
            insts = json.loads(json_data)['linked']['instructors.v1']
            courseId_instructor[courseId] = []
            for instructor in range(len(insts)):
                department = insts[instructor]['department']
                firstName = insts[instructor]['firstName']
                fullName = insts[instructor]['fullName']
                lastName = insts[instructor]['lastName']
                courseId_instructor[courseId].append([fullName, lastName, firstName, department])
            print "Successfully get instructor information"
        else:
            print "Failed to get instructor information"
        return courseId_instructor

    def get_course_materials(self, userId, courseId, cookie):
        '''

        :param userId:
        :param courseId:
        :param cookie:
        :return:
        '''

        course_material_api = 'https://www.coursera.org/api/onDemandCourseMaterials.v2?q=learner&learnerId=%s&courseId=%s&showLockedItems=true&fields=onDemandGuidedItemsProgress.v1(progressStates),onDemandGuidedNextSteps.v1(nextStep),moduleIds,modules,lessons,items,onDemandSessionMemberships.v1(sessions),onDemandCourseSchedules.v1(defaultSchedule),onDemandCourseMaterialLessons.v1(elementIds),onDemandCourseMaterialItems.v2(contentSummary,lockedStatus,itemLockedReasonCode)&includes=modules,lessons,items,onDemandSessionMemberships.v1(sessions)' % (userId, courseId)
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, course_material_api)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)

        itemId_name = {}
        lessonId_name = {}
        moduleId_name = {}

        if code == 200:
            json_data = b.getvalue()
            items = json.loads(json_data)['linked']['onDemandCourseMaterialItems.v2']
            lessons = json.loads(json_data)['linked']['onDemandCourseMaterialLessons.v1']
            modules = json.loads(json_data)['linked']['onDemandCourseMaterialModules.v1']

            for item in range(len(items)):
                itemId = items[item]['id']
                lessonId = items[item]['lessonId']
                moduleId = items[item]['moduleId']
                name = items[item]['name']
                slug = items[item]['slug']
                itemId_name[itemId] = []
                itemId_name[itemId].append([name, slug, lessonId, moduleId])

            for lesson in range(len(lessons)):
                lessonId = lessons[lesson]['id']
                moduleId = lessons[lesson]['moduleId']
                name = lessons[lesson]['name']
                slug = lessons[lesson]['slug']
                itemIds = lessons[lesson]['itemIds']
                lessonId_name[lessonId] = []
                lessonId_name[lessonId].append([name, slug, moduleId, itemIds])

            for module in range(len(modules)):
                moduleId = modules[module]['id']
                name = modules[module]['name']
                slug = modules[module]['slug']
                lessonIds = modules[module]['lessonIds']
                order = module
                moduleId_name[moduleId] = []
                moduleId_name[moduleId].append([name,slug,lessonIds,order])

        return itemId_name, lessonId_name, moduleId_name

    def get_course_material_by_slug(self,courseNameSlug,cookie):
        material_apis = 'https://www.coursera.org/api/onDemandCourseMaterials.v2/?q=slug&slug=%s&includes=modules%%2Clessons%%2CpassableItemGroups%%2CpassableItemGroupChoices%%2CpassableLessonElements%%2Citems%%2Ctracks%%2CgradePolicy&fields=moduleIds%%2ConDemandCourseMaterialModules.v1(name%%2Cslug%%2Cdescription%%2CtimeCommitment%%2ClessonIds%%2Coptional%%2ClearningObjectives)%%2ConDemandCourseMaterialLessons.v1(name%%2Cslug%%2CtimeCommitment%%2CelementIds%%2Coptional%%2CtrackId)%%2ConDemandCourseMaterialPassableItemGroups.v1(requiredPassedCount%%2CpassableItemGroupChoiceIds%%2CtrackId)%%2ConDemandCourseMaterialPassableItemGroupChoices.v1(name%%2Cdescription%%2CitemIds)%%2ConDemandCourseMaterialPassableLessonElements.v1(gradingWeight)%%2ConDemandCourseMaterialItems.v2(name%%2Cslug%%2CtimeCommitment%%2CcontentSummary%%2CisLocked%%2ClockableByItem%%2CitemLockedReasonCode%%2CtrackId%%2ClockedStatus)%%2ConDemandCourseMaterialTracks.v1(passablesCount)&showLockedItems=true' % courseNameSlug
        c = pycurl.Curl()
        b = StringIO.StringIO()

        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, material_apis)
        c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.COOKIE, cookie)
        c.perform()
        code = c.getinfo(pycurl.HTTP_CODE)

        itemId_name = {}
        lessonId_name = {}
        moduleId_name = {}

        if code == 200:
            json_data = b.getvalue()
            items = json.loads(json_data)['linked']['onDemandCourseMaterialItems.v2']
            lessons = json.loads(json_data)['linked']['onDemandCourseMaterialLessons.v1']
            modules = json.loads(json_data)['linked']['onDemandCourseMaterialModules.v1']

            for item in range(len(items)):
                itemId = items[item]['id']
                isLocked = items[item]['isLocked']
                lessonId = items[item]['lessonId']
                moduleId = items[item]['moduleId']
                name = items[item]['name']
                slug = items[item]['slug']
                typeName = items[item]['contentSummary']['typeName']
                itemId_name[itemId] = []
                itemId_name[itemId].append([name, typeName, slug, lessonId, moduleId, isLocked])

            for lesson in range(len(lessons)):
                lessonId = lessons[lesson]['id']
                moduleId = lessons[lesson]['moduleId']
                name = lessons[lesson]['name']
                slug = lessons[lesson]['slug']
                itemIds = lessons[lesson]['itemIds']
                lessonId_name[lessonId] = []
                lessonId_name[lessonId].append([name, slug, moduleId, itemIds])

            for module in range(len(modules)):
                moduleId = modules[module]['id']
                name = modules[module]['name']
                slug = modules[module]['slug']
                lessonIds = modules[module]['lessonIds']
                order = module
                moduleId_name[moduleId] = []
                moduleId_name[moduleId].append([name,slug,lessonIds,order])
        return itemId_name, lessonId_name, moduleId_name


if __name__ == '__main__':


    # create_table = CreateTables()
    # create_table.create_all_tables()

    courseNameSlug_temp = 'machine-learning'
    conn = sqlite3.connect('C:\\Users\\workshop\\Desktop\\nusdata.db')
    c = conn.cursor()
    courseNames = c.execute('select distinct(coursename) from forum').fetchall()
    conn.commit()

    with open('config.yml') as f:
        config = yaml.load(f)
    userId = config['UserId']
    # courseId = 'rc5KG0aUEeWG1w6arGoEIQ'
    database_path = config['database_path']

    conn_db = sqlite3.connect(database_path)
    conn_db.text_factory = str
    c2 = conn_db.cursor()

    #主要bug所在地
    page_analyser = PageAnalyser()
    page_analyser.login()
    cookie = page_analyser.get_cookie(courseNameSlug_temp)
    print cookie
    print "Successfully get cookie!"
    courseId_start_end = page_analyser.get_session_membership(userId=userId, cookie=cookie)
    print courseId_start_end.keys()

    count = 0
    for courseId in courseId_start_end.keys():
        count += 1
        print "Start crawling sessions and instructors for %d/%d" % (count, len(courseId_start_end.keys()))
        # write session data into table data
        startedAt, endedAt = courseId_start_end[courseId][0], courseId_start_end[courseId][1]
        c2.execute('insert or ignore into session values (?,?,?)', (courseId, startedAt, endedAt))
        # write instructor data into database
        courseId_instructor = page_analyser.get_instructors(courseId=courseId,
                                                            cookie=cookie)  # Get instructor names by courseId, saved as{courseId,[[fullName, lastName, firstName, department],[fullName, lastName, firstName, department],...],...}
        instructor_num = len(courseId_instructor[courseId])
        for i in range(instructor_num):
            [fullName, lastName, firstName, department] = courseId_instructor[courseId][i]
            c2.execute('insert or ignore into instructor values (?,?,?,?,?)',
                       (courseId, fullName, lastName, firstName, department))

    for ii in xrange(len(courseNames)):
        course = courseNames[ii]
        print 'Processing: %d/%d....'%(ii+1,len(courseNames))
        courseNameSlug = course[0]
        courseid = c.execute('select courseid from forum where coursename = ? limit 1', (courseNameSlug,)).fetchall()
        courseId = courseid[0][0]
        try:

            #write course table
            c2.execute('insert or ignore into course values (?,?,?,?)', (courseNameSlug, courseId, '', 'Coursera'))
            conn_db.commit()
            #get information

            itemId_name, lessonId_name, moduleId_name = page_analyser.get_course_materials(userId=userId, courseId=courseId, cookie=cookie)# #Get videos, slides, and excel-files
            #write item, lesson, module data into database
            itemId_name, lessonId_name, moduleId_name = page_analyser.get_course_material_by_slug(courseNameSlug=courseNameSlug, cookie=cookie)
            module_order = 0
            for moduleId in moduleId_name.keys():
                [name, slug, lessonIds, order] = moduleId_name[moduleId][0]
                c2.execute('insert or ignore into resource_module(courseNameSlug, moduleId, name, slug, module_order) values (?,?,?,?,?)', (courseNameSlug, moduleId, name, slug, module_order))
                module_order += 1
                lesson_order = 0
                for lessonId in lessonIds:
                    [name, slug, moduleId, item_ids] = lessonId_name[lessonId][0]
                    c2.execute(
                        'insert or ignore into resource_lesson(courseNameSlug, lessonId, moduleId, name, slug, lesson_order) values (?,?,?,?,?,?)',
                        (courseNameSlug, lessonId, moduleId, name, slug, lesson_order))

                    lesson_order += 1
                    item_order = 0
                    for itemId in item_ids:
                        [name, typeName, slug, lessonId, moduleId, isLocked] = itemId_name[itemId][0]
                        c2.execute('insert or ignore into resource_item(courseNameSlug, itemId, isLocked, lessonId, moduleId, name, slug, typeName, item_order) values(?,?,?,?,?,?,?,?,?)', (courseNameSlug, itemId, isLocked, lessonId, moduleId, name, slug, typeName, item_order))
                        item_order += 1
            conn_db.commit()
        except Exception,e:
            print e

    f.close()
    conn_db.close()
    page_analyser.driver.quit()
