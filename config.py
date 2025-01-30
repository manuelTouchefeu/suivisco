import os

# To generate a new secret key:
# >>> import random, string
# >>> "".join([random.choice(string.printable) for _ in range(24)])
SECRET_KEY = "#d#JCqTTW\nilK\\7m\x0bp#\tj~#H"

basedir = os.path.abspath(os.path.dirname(__file__))
APPDIR = os.path.join(basedir, 'suiviflaskapp/')

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'suivi.sqlite3')
SQLALCHEMY_DATABASE_URI = 'postgresql://suivisco:mtmc17052412@postgresql-suivisco.alwaysdata.net/suivisco_db'


SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = 3600*24*30



UPLOAD_OBS = os.path.join(basedir, 'suiviflaskapp/static/images/')
UPLOAD_BLOG_IMG = os.path.join(basedir, 'suiviflaskapp/static/blog/images/')
UPLOAD_BLOG_AUDIO = os.path.join(basedir, 'suiviflaskapp/static/blog/audio/')
UPLOAD_BLOG_VIDEO = os.path.join(basedir, 'suiviflaskapp/static/blog/video/')
UPLOAD_BLOG_DOC = os.path.join(basedir, 'suiviflaskapp/static/blog/docs/')
UPLOAD_VISITOR_DATA = os.path.join(basedir, 'suiviflaskapp/static/blog/visitor-data/')
PDF = os.path.join(basedir, 'suiviflaskapp/static/pdf/')
DIARY = os.path.join(basedir, 'suiviflaskapp/diary/')

# Pour éviter le chemin absolu dans les templates
BLOG_IMG = '/static/blog/images/'
BLOG_AUDIO = '/static/blog/audio/'
BLOG_VIDEO = '/static/blog/video/'
BLOG_DOC = '/static/blog/docs/'
VISITOR_DATA = '/static/blog/visitor-data'
OBS = '/static/images/'

MAIL_SERVER = 'smtp-suivisco.alwaysdata.net'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'suivisco@alwaysdata.net'
MAIL_PASSWORD = 'mtmc17052412'
#MAIL_DEFAULT_SENDER = 'suivisco@alwaysdata.net'
