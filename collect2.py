import psycopg2
psy = psycopg2.connect(user="suivisco",
                       password="mtmc17052412",
                       host="postgresql-suivisco.alwaysdata.net",
                       database="suivisco_bdd")
psyconn = psy.cursor()

lite = psycopg2.connect(user="suivisco",
                       password="mtmc17052412",
                       host="postgresql-suivisco.alwaysdata.net",
                       database="suivisco_db")
connlite = lite.cursor()


psyconn.execute("SELECT id, name FROM cycle")
for l in psyconn.fetchall():
    sql = "INSERT INTO cycle (id, name) VALUES (%s, '%s')" % (l[0], l[1])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('cycle_id_seq', select max(id) from cycle)")
lite.commit()



psyconn.execute("SELECT id, name, cycle_id, position from field")
for l in psyconn.fetchall():
    sql = "INSERT INTO field (id, name, cycle_id, position) VALUES (%s, '%s', %s, %s)" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('field_id_seq', select max(id) from field")
lite.commit()



psyconn.execute("SELECT id, name, field_id, position from skill")
for l in psyconn.fetchall():
    sql = "INSERT INTO skill (id, name, field_id, position) VALUES (%s, '%s', %s, %s)" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('skill_id_seq', select max(id) from skill)")
lite.commit()



psyconn.execute("SELECT id, name, skill_id, level, position from observable")
for l in psyconn.fetchall():
    sql = "INSERT INTO observable (id, name, skill_id, level, position) VALUES (%s, '%s', %s, %s, %s)" % (l[0], l[1], l[2], l[3], l[4])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('observable_id_seq', select max(id) from observable)")
lite.commit()



psyconn.execute("SELECT id, name from classroom")
for l in psyconn.fetchall():
    sql = "INSERT INTO classroom (id, name) VALUES (%s, '%s')" % (l[0], l[1])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('classroom_id_seq', select max(id) from classroom)")
lite.commit()



psyconn.execute("SELECT id, lastname, firstname, gender, birthdate, classroom_id, speed from child")
for l in psyconn.fetchall():
    sql = "INSERT INTO child (id, lastname, firstname, gender, birthdate, classroom_id, speed) VALUES (%s, '%s', '%s', '%s', '%s', %s, %s)"\
          % (l[0], l[1], l[2], l[3], l[4], l[5], l[6])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('obs_child_id_seq', select max(id) from obs_child)")
lite.commit()



psyconn.execute("SELECT id, child_id, content, date, author, grp from comment")
for l in psyconn.fetchall():
    sql = "INSERT INTO comment (id, child_id, content, date, author, grp) VALUES (%s, %s, '%s', '%s', '%s', '%s')"\
          % (l[0], l[1], l[2], l[3], l[4], l[5])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('obs_child_id_seq', select max(id) from obs_child)")
lite.commit()



psyconn.execute("SELECT obs_id, classroom_id, image from obs_classroom_image")
for l in psyconn.fetchall():
    sql = "INSERT INTO obs_classroom_image (obs_id, classroom_id, image) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('obs_child_id_seq', select max(id) from obs_child)")
lite.commit()



psyconn.execute("SELECT obs_id, child_id, image, date from obs_child")
for l in psyconn.fetchall():
    sql = "INSERT INTO obs_child (obs_id, child_id, image, date) VALUES (%s, %s, '%s', '%s')" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('obs_child_id_seq', select max(id) from obs_child)")
lite.commit()




psyconn.execute("SELECT id, classroom_id, name, description FROM category")
for l in psyconn.fetchall():
    sql = "INSERT INTO category (id, classroom_id, name, description) VALUES (%s, %s, '%s', '%s')" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('category_id_seq', select max(id) from category)")
lite.commit()



psyconn.execute("SELECT id, classroom_id, title, content, date, image, is_published, is_editable from article")
for l in psyconn.fetchall():
    sql = "INSERT INTO article (id, classroom_id, title, content, date, image, is_published, is_editable) VALUES (%s, '%s', '%s', '%s', '%s', '%s', %s, %s)"\
          % (l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('article_id_seq', select max(id) from article)")
lite.commit()


    
psyconn.execute("SELECT id, lastname, firstname, email, password_hash, is_staff, classroom_id from public.user")
for l in psyconn.fetchall():
    sql = "INSERT INTO public.user (id, lastname, firstname, email, password_hash, is_staff, classroom_id) VALUES (%s, '%s', '%s', '%s', '%s', %s, %s)"\
          % (l[0], l[1], l[2], l[3], l[4], l[5], l[6])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('user_id_seq', select max(id) from user)")
lite.commit()
    



psyconn.execute("SELECT id, lastname, firstname, email, password_hash, is_active from visitor")
for l in psyconn.fetchall():
    sql = "INSERT INTO visitor (id, lastname, firstname, email, password_hash, is_active) VALUES (%s, '%s', '%s', '%s', '%s', %s)"\
          % (l[0], l[1], l[2], l[3], l[4], l[5])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('visitor_id_seq', select max(id) from visitor)")
lite.commit()




psyconn.execute("SELECT id, article_id, visitor_id, user_id, content, datetime, author from article_comment")
for l in psyconn.fetchall():
    v = 'NULL' if l[2] is None else l[2]
    u = 'NULL' if l[3] is None else l[3]
    sql = "INSERT INTO article_comment (id, article_id, visitor_id, user_id, content, datetime, author) VALUES (%s, %s, %s, %s, '%s', '%s', '%s')"\
          % (l[0], l[1], v, u, l[4], l[5], l[6])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('article_comment_id_seq', select max(id) from article_comment)")
lite.commit()




psyconn.execute("SELECT id, classroom_id, filename FROM blog_audio")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_audio (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('blog_audio_id_seq', select max(id) from blog_audio)")
lite.commit()



psyconn.execute("SELECT id, classroom_id, filename FROM blog_video")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_video (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('blog_video_id_seq', select max(id) from blog_video)")
lite.commit()



psyconn.execute("SELECT id, classroom_id, filename FROM blog_image")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_image (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('blog_image_id_seq', select max(id) from blog_image)")
lite.commit()


psyconn.execute("SELECT id, classroom_id, filename FROM blog_doc")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_doc (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('blog_doc_id_seq', select max(id) from blog_image)")
lite.commit()



psyconn.execute("SELECT id, classroom_id, visitor_id, remote_addr, datetime from blog_visit")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_visit (id, classroom_id, visitor_id, remote_addr, datetime) VALUES (%s, %s, %s, '%s', '%s')"\
          % (l[0], l[1], l[2],l[3], l[4])
    print(sql)
    connlite.execute(sql)
connlite.execute("SELECT setval('blog_visit_id_seq', select max(id) from blog_visit)")
lite.commit()





