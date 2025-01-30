import psycopg2
lite = psycopg2.connect(user="suivisco",
                       password="mtmc17052412",
                       host="postgresql-suivisco.alwaysdata.net",
                       database="suivisco_bdd")
connlite = lite.cursor()

sql = 'SELECT id, content FROM article'
connlite.execute(sql)
for line in connlite.fetchall():
    l = line[1].replace('/static/images/blog/', '/static/blog/images/')
    l = l.replace('/static/audio/', '/static/blog/audio/')
    l = l.replace('/static/video/', '/static/blog/video/')
    print(l)
    sql = """UPDATE article set content='%s' where id=%s""" % (l, line[0])
    print(sql)
    connlite.execute(sql)
    lite.commit()

# psql -h postgresql-suivisco.alwaysdata.net -U suivisco -W -d suivi_bdd

