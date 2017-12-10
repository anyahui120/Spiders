#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Author  : Ann
# @Time    :

import sqlite3

database = '../courseraD.db'
conn = sqlite3.connect(database)
c = conn.cursor()


# For modules

# where resource_type = module(week): https://www.coursera.org/learn/accounting-analytics/home/week/1
prefix = 'https://www.coursera.org/learn'
suffix = 'home/week'
select_type = c.execute("""select rowid, courseNameSlug, module_order from resource_module""").fetchall()
count = 0
for row in select_type:
    count += 1
    row_id, course_name_slug, week_num = row[0], row[1], row[2]
    actualURL = prefix + '/' + course_name_slug + '/' + suffix + '/' + str(week_num+1)
    c.execute('update or ignore resource_module set actualURL = (?) where rowid = (?)', (actualURL,row_id,))
    print 'Processing modules: %d/%d ...'%(count, len(select_type))
conn.commit()

# For lessons

select_type = c.execute("""select rowid, courseNameSlug, moduleId from resource_lesson""").fetchall()
count = 0
for row in select_type:
    count += 1
    row_id, course_name_slug, moduleId = row[0], row[1], row[2]
    lesson_module_order = c.execute('select module_order from resource_module where moduleId = ?', (moduleId,)).fetchone()
    week_num = lesson_module_order
    actualURL = prefix + '/' + course_name_slug + '/' + suffix + '/' + str(week_num[0]+1)
    c.execute('update or ignore resource_lesson set actualURL = (?) where rowid = (?)', (actualURL,row_id,))
    print 'Processing lessons: %d/%d ...'%(count, len(select_type))
conn.commit()

# For videos/lectures
# https://www.coursera.org/learn/accounting-analytics/lecture/ITOeL/module-1-overview-1-0
prefix = 'https://www.coursera.org/learn'
select_type = c.execute("""select rowid, courseNameSlug,typeName, itemId, slug  from resource_item""").fetchall()
count = 0
for row in select_type:
    count += 1
    row_id, courseNameSlug, typeName, itemId, slug = row[0], row[1], row[2], row[3], row[4]
    actualURL = prefix + '/' + courseNameSlug + '/' +typeName + '/' + itemId + '/' + suffix + '/' + slug
    c.execute('update or ignore resource_item set actualURL = (?) where rowid = (?)', (actualURL,row_id,))
    print 'Processing lessons: %d/%d ...'%(count, len(select_type))
conn.commit()

conn.close()





