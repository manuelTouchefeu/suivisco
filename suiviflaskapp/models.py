import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.collections import attribute_mapped_collection
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .views import app
from .utils import personalize

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# Create database connection object
db = SQLAlchemy(app)


login = LoginManager(app)
login.login_view = '/login'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(200), nullable=False)
    firstname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    is_staff = db.Column(db.Boolean(), default=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='SET NULL'))
    classroom = db.relationship('ClassRoom', backref=db.backref('user', uselist=False))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)


class ClassRoom(db.Model):
    __tablename__ = 'classroom'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


class Child(db.Model):
    __tablename__ = 'child'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.CHAR, db.CheckConstraint('gender = \'F\' or gender = \'M\''), nullable=False)
    lastname = db.Column(db.String(200), nullable=False)
    firstname = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    speed = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship('Comment', backref='child', order_by='desc(Comment.date)', lazy=True, cascade='all,delete')
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='SET NULL'))

    field = {}

    def group(self):
        janvier = False
        # if 1 <= datetime.today().month < 8:
        if datetime.today().month < 7 or (datetime.today().month == 7 and datetime.today().day < 5):
            janvier = True
        diff = datetime.today().year - self.birthdate.year + self.speed
        if diff == 11:
            return "CM2"
        elif diff == 10:
            return "CM1" if janvier else "CM2"
        elif diff == 9:
            return "CE2" if janvier else "CM1"
        elif diff == 8:
            return "CE1" if janvier else "CE2"
        elif diff == 7:
            return "CP" if janvier else "CE1"
        elif diff == 6:
            return "GS" if janvier else "CP"
        elif diff == 5:
            return "MS" if janvier else "GS"
        elif diff == 4:
            return "PS" if janvier else "MS"
        elif diff == 3:
            return "TPS" if janvier else "PS"
        elif diff == 2:
            return "TPS"
        else:
            return "TPS"

    def cycle(self):
        if self.age() < 3:
            return 1
        elif self.age() > 5:
            return 3
        else:
            return 2

    def age(self):
        return {"TPS": 0, "PS": 0, "MS": 1, "GS": 2, "CP": 3, "CE1": 4, "CE2": 5,
                "CM1": 6, "CM2": 7}[self.group()]

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.String(), nullable=False)
    grp = db.Column(db.String(5), nullable=False)
    author = db.Column(db.String(), nullable=False)
    date = db.Column(db.Date, default=datetime.now())


class Cycle(db.Model):
    __tablename__ = 'cycle'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    fields = db.relationship('Field',
                             collection_class=attribute_mapped_collection('position'),
                             cascade='all, delete-orphan')


class Field(db.Model):
    __tablename__ = 'field'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    position = db.Column(db.Integer(), nullable=False)
    cycle_id = db.Column(db.Integer(), db.ForeignKey('cycle.id', ondelete='CASCADE'), nullable=False)
    skills = db.relationship('Skill',
                             collection_class=attribute_mapped_collection('position'),
                             cascade='all, delete-orphan')


class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    position = db.Column(db.Integer(), nullable=False)
    field_id = db.Column(db.Integer(), db.ForeignKey('field.id', ondelete='CASCADE'), nullable=False)
    observables = db.relationship('Observable',
                                  collection_class=attribute_mapped_collection('position'),
                                  cascade='all, delete-orphan')


class Observable(db.Model):
    __tablename__ = 'observable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    position = db.Column(db.Integer(), nullable=False)
    level = db.Column(db.Integer(), nullable=False)
    skill_id = db.Column(db.Integer(), db.ForeignKey('skill.id', ondelete='CASCADE'), nullable=False)


class ObsClassroomImage(db.Model):
    __tablename__ = 'obs_classroom_image'
    obs_id = db.Column(db.Integer, db.ForeignKey('observable.id', ondelete='CASCADE'), primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'), primary_key=True)
    image = db.Column(db.String())


class ObsClassroomDone(db.Model):
    __tablename__ = 'obs_classroom_done'
    obs_id = db.Column(db.Integer, db.ForeignKey('observable.id', ondelete='CASCADE'), primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'), primary_key=True)
    done = db.Column(db.Date, default=datetime.now())


class ObsChild(db.Model):
    __tablename__ = 'obs_child'
    obs_id = db.Column(db.Integer, db.ForeignKey('observable.id', ondelete='CASCADE'), primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id', ondelete='CASCADE'), primary_key=True)
    image = db.Column(db.String())
    date = db.Column(db.Date, default=datetime.now())
    ability = db.Column(db.Integer, nullable=False, default=0)


class Visitor(db.Model):
    __tablename__ = 'visitor'
    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(200), nullable=False)
    firstname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean(), default=False)
    comments = db.relationship('ArticleComment', backref='visitor', lazy=True, cascade='all,delete')

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        password = hashlib.sha256(password.encode()).hexdigest()
        return password == self.password_hash

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'), nullable=False)


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, default=datetime.now())
    image = db.Column(db.String())
    is_published = db.Column(db.Boolean(), default=False)
    is_editable = db.Column(db.Boolean(), default=False)
    comments = db.relationship('ArticleComment',
                               order_by='ArticleComment.id.desc()',
                               backref='article',
                               lazy=True, cascade='all,delete')
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id', ondelete='SET NULL'))
    category = db.relationship('Category', backref=db.backref('article', uselist=False))


class ArticleComment(db.Model):
    __tablename__ = 'article_comment'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)
    # author: visitor xor user
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.String(), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.now())
    author = db.Column(db.String(), nullable=False)
    is_public = db.Column(db.Boolean(), default=False, nullable=False)
    answers = db.relationship('ArticleCommentAnswer',
                               order_by='ArticleCommentAnswer.id.desc()',
                               backref='article_comment',
                               lazy=True, cascade='all,delete')


class ArticleCommentAnswer(db.Model):
    __tablename__ = 'article_comment_answer'
    id = db.Column(db.Integer, primary_key=True)
    article_comment_id = db.Column(db.Integer, db.ForeignKey('article_comment.id', ondelete='CASCADE'), nullable=False)
    # author: visitor xor user
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.String(), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.now())
    author = db.Column(db.String(), nullable=False)


class BlogImage(db.Model):
    __tablename__ = 'blog_image'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    filename = db.Column(db.String())


class BlogAudio(db.Model):
    __tablename__ = 'blog_audio'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    filename = db.Column(db.String())


class BlogVideo(db.Model):
    __tablename__ = 'blog_video'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    filename = db.Column(db.String())


class BlogDoc(db.Model):
    __tablename__ = 'blog_doc'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    filename = db.Column(db.String())
    preview = db.Column(db.String())


class BlogVisit(db.Model):
    __tablename__ = 'blog_visit'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, nullable=False)
    remote_addr = db.Column(db.String())
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    datetime = db.Column(db.DateTime, default=datetime.now())

    def get_date(self):
        return self.datetime.strftime("%d/%m/%Y")

    def get_time(self):
        return self.datetime.strftime("%H:%M:%S")


class BlogVisio(db.Model):
    __tablename__ = 'blog_visio'
    id = db.Column(db.Integer, primary_key=True)
    is_available = db.Column(db.Boolean(), default=False, nullable=False)
    ref = db.Column(db.Integer(), nullable=False)


class TimeTable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    filename = db.Column(db.String())


class Diary(db.Model):
    __tablename__ = 'diary'
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id', ondelete='CASCADE'))
    filename = db.Column(db.String())
    date = db.Column(db.Date, nullable=False, unique=True)

db.create_all()


########################## RAW SQL ############################################
class FieldRaw:
    def __init__(self, dom_id, name, position):
        self.id = dom_id
        self.name = name
        self.position = position
        self.skills = {}


class SkillRaw:
    def __init__(self, field_id, skill_id, name, position):
        self.field_id = field_id
        self.id = skill_id
        self.name = name
        self.position = position
        self.observables = {}


class ObservableRaw:
    def __init__(self, skill_id, obs_id, name, level, position, done, image=None):
        self.skill_id = skill_id
        self.id = obs_id
        self.name = name
        self.level = level # 0 -> PS; 1 -> MS; 2 -> GS etc...
        self.position = position
        self.image = image
        self.done = done
        self.children = []

    def _get_levelstr(self):
        return {0: 'PS', 1: 'MS', 2: 'GS', 3: 'CP',
                4: 'CE1', 5: 'CE2', 6: 'CM1', 7: 'CM2', 8:'6ème', 20: 'tous', 50: 'tous', 80: 'tous'}[self.level]
    levelstr = property(_get_levelstr)

class ObservableChild(ObservableRaw):
    def __init__(self, skill_id, obs_id, name, age, level, position, done, ability=None, image_child=None, date=None, image=None):
        super().__init__(skill_id, obs_id, name, level, position, done, image)
        self.image_child = image_child
        self.status = int()
        self.date = date
        self.ability = ability
        self.age = age # for pdf simple

        if date is not None:
            self.status = self.ability
        elif age > self.level or self.done and age == self.level:
            self.status = 7
        elif self.level in [20, 50, 80] and self.done:
            self.status = 7
        elif age == self.level or self.level in [20, 50, 80]:
            self.status = 6
        elif self.level > age:
            self.status = 5
        """"
        if date is not None:
            self.status = 0
        elif age > self.level or self.done and age == self.level:
            self.status = 1
        elif self.level in [20, 50, 80] and self.done:
            self.status = 1
        elif age == self.level or self.level in [20, 50, 80]:
            self.status = 2
        elif self.level > age:
            self.status = 3
        """
    def _get_status(self):
        #return {0: 'ok', 1: 'alert', 2: 'next', 3: 'pass'}[self.status]
        return  {0: 'red', 1: 'orange', 2: 'blue', 3: 'lightgreen',
                 4: 'green', 5: 'pass', 6: 'next', 7: 'required'}[self.status]
    status_s = property(_get_status)


engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], {})


def get_field(field_id, classroom_id):
    with engine.connect() as con:
        sql = 'SELECT field.id, field.name, field.position,\
               skill.id, skill.name, skill.position, \
               observable.id, observable.name, observable.level, observable.position,\
               obs_classroom_image.image, obs_classroom_done.done \
               FROM field \
               LEFT JOIN skill \
               ON skill.field_id = field.id \
               LEFT JOIN observable \
               ON observable.skill_id = skill.id \
               LEFT JOIN obs_classroom_image \
               ON obs_classroom_image.obs_id = observable.id \
               AND obs_classroom_image.classroom_id = %s \
               LEFT JOIN obs_classroom_done \
               ON obs_classroom_done.obs_id = observable.id \
               AND obs_classroom_done.classroom_id = %s \
               WHERE field.id = %s' % (classroom_id, classroom_id, field_id)
        q = con.execute(sql).fetchall()
        f = FieldRaw(q[0][0], q[0][1], q[0][2])
        if q[0][3] is None:
            return f
        for row in q:
            if row[5] not in f.skills.keys():
                s = SkillRaw(f.id, row[3], row[4], row[5])
                f.skills[s.position] = s
            if row[6]:
                o = ObservableRaw(row[3], row[6], row[7], row[8], row[9], row[11], row[10])
                f.skills[row[5]].observables[o.position] = o
        return f


def get_field_child(child, field_id):
    with engine.connect() as con:
        # skill_id, obs_id, name, age, level, position, image_child=None, date=None
        sql = 'SELECT field.id, field.name, field.position,\
               skill.id, skill.name, skill.position, \
               observable.id, observable.name, observable.level, observable.position,\
               obs_child.image, obs_child.date, obs_child.ability,\
               obs_classroom_image.image, obs_classroom_done.done\
               FROM field \
               LEFT JOIN skill \
               ON skill.field_id = field.id \
               LEFT JOIN observable \
               ON observable.skill_id = skill.id \
               LEFT JOIN obs_child \
               ON obs_child.obs_id = observable.id \
               AND obs_child.child_id = %s \
               LEFT JOIN obs_classroom_image \
               ON obs_classroom_image.obs_id = observable.id \
               AND obs_classroom_image.classroom_id = %s \
               LEFT JOIN obs_classroom_done \
               ON obs_classroom_done.obs_id = observable.id \
               AND obs_classroom_done.classroom_id = %s \
               WHERE field.id = %s' % (child.id, child.classroom_id, child.classroom_id, field_id)
        q = con.execute(sql).fetchall()
        f = FieldRaw(q[0][0], q[0][1], q[0][2])
        if q[0][3] is None:
            return f
        for row in q:
            if row[5] not in f.skills.keys():
                s = SkillRaw(f.id, row[3], row[4], row[5])
                f.skills[s.position] = s
            if row[6]:
                #def __init__(self, skill_id, obs_id, name, age, level, position, done, ability, image_child=None, date=None, image=None):
                o = ObservableChild(row[3], row[6], personalize(row[7], child), child.age(),
                                    row[8], row[9], row[14], row[12], row[10], row[11], row[13])
                f.skills[row[5]].observables[o.position] = o
        return f


def cycle(age):
    if age < 3:
        return 1
    elif age > 5:
        return 3
    else:
        return 2


def age(grp):
    return {"TPS": 0, "PS": 0, "MS": 1, "GS": 2, "CP": 3, "CE1": 4, "CE2": 5,
            "CM1": 6, "CM2": 7}[grp]


########################## POPULATE ###########################################
# Create Admin User

"""
if not User.query.filter(User.email == 'manuel.touchefeu@gmail.com').first():
    user = User(firstname='Manuel',
                lastname='Touchefeu',
                email='manuel.touchefeu@gmail.com',
                is_staff=True)

    user.set_password('jojo')
    print(user)
    db.session.add(user)
    db.session.commit()

# Create cycles
if not Cycle.query.get(1):
    cycle = Cycle(id=1, name='Cycle des apprentissages premiers')
    db.session.add(cycle)
    db.session.commit()
if not Cycle.query.get(2):
    cycle = Cycle(id=2, name='Cycle des apprentissages fondamentaux')
    db.session.add(cycle)
    db.session.commit()
if not Cycle.query.get(3):
    cycle = Cycle(id=3, name='Cycle de consolidation')
    db.session.add(cycle)
    db.session.commit()


# Create fields

import sqlite3
jojo = sqlite3.connect("source.sqlite3")
conn = jojo.cursor()


if not Field.query.get(1):
    domaines = conn.execute("SELECT id, nom, cycle, position FROM domaines")
    domaines = conn.fetchall()
    for e in domaines:
        domaine = Field(id=e[0],name=e[1], cycle_id=e[2], position=e[3])
        db.session.add(domaine)
        db.session.commit()



if not Skill.query.get(1):
    competence = conn.execute("SELECT id, nom, domaine, position FROM competences")
    competences = conn.fetchall()
    for e in competences:
        comp = Skill(id=e[0],name=e[1], field_id=e[2], position=e[3])
        db.session.add(comp)
        db.session.commit()


if not Observable.query.get(1):
    observables = conn.execute("SELECT id, nom, competence, niveau, position FROM observables")
    observables = conn.fetchall()
    for e in observables:
        obs = Observable(id=e[0],name=e[1], skill_id=e[2], level=e[3], position=e[4])
        db.session.add(obs)
        db.session.commit()


if not ClassRoom.query.get(1):
    classes = conn.execute("SELECT id, nom FROM classes")
    classes = conn.fetchall()
    for e in classes:
        classe = ClassRoom(id=e[0],name=e[1])
        db.session.add(classe)
        db.session.commit()


if not Child.query.get(1):
    enfs = conn.execute("SELECT id, nom, prenom, classe, vitesse, sexe, date FROM enfants")
    enfs = conn.fetchall()
    for e in enfs:
        enf = Child(id=e[0],lastname=e[1], firstname=e[2],
                    classroom_id=e[3], speed=e[4], gender=e[5], _birthdate=datetime.fromtimestamp(e[6]))
        db.session.add(enf)
        db.session.commit()

if not Comment.query.get(1):
    com = conn.execute("SELECT id, enfant_id , commentaire, author, groupe, date FROM commentaires")
    com = conn.fetchall()
    for e in com:
        c = Comment(id=e[0],child_id=e[1], content=e[2],
                    author=e[3], group=e[4], _date=datetime.fromtimestamp(e[5]))
        db.session.add(c)
        db.session.commit()

if not Article.query.get(1):
    com = conn.execute("SELECT id, classe, title, text, status, image, date FROM blogs")
    com = conn.fetchall()
    for e in com:
        c = Article(id=e[0], classroom_id=e[1], title=e[2],
                    content=e[3], is_published=False, image=e[5], _date=datetime.fromtimestamp(e[6]))
        db.session.add(c)
        db.session.commit()

"""
