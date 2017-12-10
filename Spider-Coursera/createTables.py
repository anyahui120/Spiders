#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Time    : 7/18/2017 10:49 AM
# @Author  : Ann
# @Site    : 
# @File    :
# @Software: PyCharm

import sqlite3
import yaml

class CreateTables:
    """
    This class is for writing json format data into SQLite database.
    """
    def __init__(self):
        """
            Initial the connection to SQLite database.
        """
        with open('sql.yml') as f:
            self.sql = yaml.load(f)
        f.close()
        self.conn = sqlite3.connect(self.sql['database_path'])
        self.conn.text_factory = str
        self.c = self.conn.cursor()


    def create_instructor_table(self):
        """
        Create table instructor, columns are courseId, fullName, lastName, firstName, department
        :return: 100
        """
        self.c.execute('drop table if exists instructor')
        create_inst_table = self.sql['create_instructor_table']
        self.c.execute(create_inst_table)
        self.conn.commit()
        return 100

    def create_session_table(self):
        """
        Create table session, columns are courseId, startedAt, endedAt
        :return: 100
        """
        self.c.execute('drop table if exists session')
        create_sess_table = self.sql['create_session_table']
        self.c.execute(create_sess_table)
        self.conn.commit()
        return 100

    def create_item_table(self):
        """
        Create table item, columns are courseNameSlug, itemId, isLocked, lessonId, moduleId, name, slug, typeName, actualURL
        :return: 100
        """
        self.c.execute('drop table if exists resource_item')
        create_item_table = self.sql['create_item_table']
        self.c.execute(create_item_table)
        self.conn.commit()
        return 100

    def create_lesson_table(self):
        """
        Create table lesson, columns are courseNameSlug, lessonId, moduleId, name, slug, actualURL
        :return:
        """
        self.c.execute('drop table if exists resource_lesson')
        create_lesson_table = self.sql['create_lesson_table']
        self.c.execute(create_lesson_table)
        self.conn.commit()
        return 100

    def create_module_table(self):
        """
        Create table module, columns are
        :return: courseNameSlug, moduleId, name, slug, order, actualURL
        """
        self.c.execute('drop table if exists resource_module')
        create_module_table = self.sql['create_module_table']
        self.c.execute(create_module_table)
        self.conn.commit()
        return 100

    def create_all_tables(self):
        """
        Create all tables conveniently.
        :return:
        """
        self.create_session_table()
        self.create_item_table()
        self.create_instructor_table()
        self.create_lesson_table()
        self.create_module_table()
        self.conn.commit()
        self.conn.close()