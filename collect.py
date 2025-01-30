from datetime import datetime

#import sqlite3
#lite = sqlite3.connect("collect.sqlite3")
#connlite = lite.cursor()

import psycopg2
psy = psycopg2.connect(user="suivi",
                       password="mtmc17052412",
                       host="postgresql-suivi.alwaysdata.net",
                       database="suivi_bdd")
psyconn = psy.cursor()

lite = psycopg2.connect(user="suivisco",
                       password="mtmc17052412",
                       host="postgresql-suivisco.alwaysdata.net",
                       database="suivisco_bdd")
connlite = lite.cursor()

def check_text(text):
    text = text.strip()
    text = text.replace("'", "’")
    return text


psyconn.execute("SELECT id, nom FROM cycles")
for l in psyconn.fetchall():
    sql = "INSERT INTO cycle (id, name) VALUES (%s, '%s')" % (l[0], l[1])
    print(sql)
    connlite.execute(sql)
lite.commit()


psyconn.execute("SELECT id, nom, cycle, position from domaines")
for l in psyconn.fetchall():
    sql = "INSERT INTO field (id, name, cycle_id, position) VALUES (%s, '%s', %s, %s)" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
lite.commit()


psyconn.execute("SELECT id, nom, domaine, position from competences")
for l in psyconn.fetchall():
    sql = "INSERT INTO skill (id, name, field_id, position) VALUES (%s, '%s', %s, %s)" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, nom, competence, niveau, position from observables")
for l in psyconn.fetchall():
    sql = "INSERT INTO observable (id, name, skill_id, level, position) VALUES (%s, '%s', %s, %s, %s)" % (l[0], l[1], l[2], l[3], l[4])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, nom from classes")
for l in psyconn.fetchall():
    sql = "INSERT INTO classroom (id, name) VALUES (%s, '%s')" % (l[0], l[1])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, nom, prenom, sexe, date, classe, vitesse from enfants")
for l in psyconn.fetchall():
    sql = "INSERT INTO child (id, lastname, firstname, gender, birthdate, classroom_id, speed) VALUES (%s, '%s', '%s', '%s', '%s', %s, %s)"\
          % (l[0], l[1], l[2], l[3], l[4], l[5], l[6])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, enfant_id, commentaire, date, author, groupe from commentaires")
for l in psyconn.fetchall():
    sql = "INSERT INTO comment (id, child_id, content, date, author, grp) VALUES (%s, %s, '%s', '%s', '%s', '%s')"\
          % (l[0], l[1], l[2], l[3], l[4], l[5])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT obs, usr, image from obs_user_image")
for l in psyconn.fetchall():
    if l[1] == 7: cr = 2
    if l[1] == 8: cr = 3
    if l[1] == 2: cr = 1
    sql = "INSERT INTO obs_classroom_image (obs_id, classroom_id, image) VALUES (%s, %s, '%s')" % (l[0], cr, l[2])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT obs, enfant, image, date from observables_e")
for l in psyconn.fetchall():
    sql = "INSERT INTO obs_child (obs_id, child_id, image, date) VALUES (%s, %s, '%s', '%s')" % (l[0], l[1], l[2], l[3])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, classe, title, text, date, image, status from blogs")
for l in psyconn.fetchall():
    sql = "INSERT INTO article (id, classroom_id, title, content, date, image, is_published, is_editable) VALUES (%s, '%s', '%s', '%s', '%s', '%s', %s, %s)"\
          % (l[0], l[1], check_text(l[2]), check_text(l[3]), l[4], l[5], True, False)
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, classe, sound FROM blogs_sounds")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_audio (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, classe, video FROM blogs_videos")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_video (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
lite.commit()


psyconn.execute("SELECT id, classe, image FROM blogs_images")
for l in psyconn.fetchall():
    sql = "INSERT INTO blog_image (id, classroom_id, filename) VALUES (%s, %s, '%s')" % (l[0], l[1], l[2])
    print(sql)
    connlite.execute(sql)
lite.commit()

psyconn.execute("SELECT id, classe, visitor_id, remote_addr, date, time from blogs_stats")
for l in psyconn.fetchall():
    date = datetime.combine(l[4], l[5])
    print(date)
    sql = "INSERT INTO blog_visit (id, classroom_id, visitor_id, remote_addr, datetime) VALUES (%s, %s, %s, '%s', '%s')"\
          % (l[0], l[1], l[2],l[3], date)
    print(sql)
    connlite.execute(sql)
lite.commit()

