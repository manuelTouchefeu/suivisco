import json
import string
import shutil
import random
import re
import os
import math
import pickle
import datetime
from copy import deepcopy
from flask import Flask, render_template, request, redirect, flash, url_for, send_file, make_response, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Mail, Message
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
# from preview_generator.manager import PreviewManager

from .utils import process_image, rotate_image, check_text
from .pdf import build_pdf, build_diary, build_tt, build_tasks, build_obs_table

app = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']
mail = Mail(app)

from .models import db, User, Cycle, Field, Skill, get_field, get_field_child, \
    Observable, Child, ObsChild, ClassRoom, ObsClassroomImage, Comment, Article, \
    BlogAudio, BlogImage, BlogVideo, BlogDoc, BlogVisit, Visitor, ArticleComment, ArticleCommentAnswer, BlogVisio, \
    TimeTable, Diary, Category, ObsClassroomDone, \
    cycle, age


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Echec de l\'authentification')
            return render_template('login.html')
        login_user(user, remember=True)
        if current_user.classroom_id:
            return redirect('/observables')
        else:
            flash('Vous êtes connecté, %s. Mais vous n\'avez pas encore de classe!' % current_user)
            return render_template('login.html')
    return render_template('login.html')


@app.route('/lost-password', methods=['GET', 'POST'])
def lost_password():
    if request.method == 'POST':
        passwd = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
        msg = Message(subject='Mot de passe',
                      sender=app.config.get('MAIL_USERNAME'),
                      recipients=[request.form['email']],  # replace with your email for testing
                      body='Voici votre nouveau mot de passe: %s' % passwd)
        mail.send(msg)
        user = User.query.filter_by(email=request.form['email']).first()
        user.set_password(passwd)
        db.session.commit()
        flash('Un nouveau mot de passe vous a été envoyé. Il est recommandé de le changer!')
        return redirect('/login')
    return render_template('lost-password.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        if request.form['password'] != request.form['password2']:
            flash('Il y a une erreur sur le mot de passe!')
        else:
            current_user.set_password(request.form['password'])
            db.session.commit()
            flash('Votre mot de passe a été modifié.')
    return render_template('account.html')


@app.route('/')
def home():
    return redirect('/observables')


# __________________________________OBSERVABLES________________________________________________________
@app.route('/observables/')  # ?cycle=id&field=id
@login_required
def observables():
    children = Child.query.filter_by(classroom_id=current_user.classroom_id).order_by(Child.birthdate.desc())
    cycles = []
    for c in children:
        if c.cycle() not in cycles:
            cycles.append(c.cycle())
    cycle_id = int(request.args.get('cycle')) if request.args.get('cycle') else min(cycles)
    cycle = Cycle.query.get(cycle_id)
    field_id = int(request.args.get('field')) if request.args.get('field') \
        else min([f.id for f in cycle.fields.values()])

    field = get_field(field_id, current_user.classroom.id)
    jojo = ObsClassroomImage.query.all()[0]

    # reset available
    reset_available = True if datetime.datetime.now().month in [7, 8] else False
    return render_template('observables.html',
                           cycles=cycles,
                           cycle=cycle,
                           field=field, jojo=jojo,
                           reset_available = reset_available)


@app.route('/observables/upload', methods=['POST'])  # ajax
@login_required
def observables_upload():
    print(request.form)
    name = process_image(request.files.get('file'),
                         app.config['UPLOAD_OBS'])
    if name:
        if request.form.get('update') == 'false':
            img = ObsClassroomImage(obs_id=int(request.form.get('obs_id')),
                                    classroom_id=current_user.classroom.id,
                                    image=name)
            db.session.add(img)
        else:
            img = ObsClassroomImage.query.filter_by(obs_id=int(request.form.get('obs_id')),
                                                    classroom_id=current_user.classroom.id).one()
            img.image = name
        db.session.commit()
        return name
    return "error"


@app.route('/upload-from-blog', methods=['POST'])
@login_required
def upload_from_blog():
    shutil.copy2('%s%s' % (app.config['UPLOAD_BLOG_IMG'], request.json['filename']),
                 app.config['UPLOAD_OBS'])
    if not request.json['update']:
        img = ObsClassroomImage(obs_id=int(request.json['obs_id']),
                                classroom_id=current_user.classroom.id,
                                image=request.json['filename'])
        db.session.add(img)
    else:
        img = ObsClassroomImage.query.filter_by(obs_id=int(request.json['obs_id']),
                                                classroom_id=current_user.classroom.id).one()
        img.image = request.json['filename']
    db.session.commit()
    return json.dumps({'filename': img.image})


@app.route('/observables/del_image', methods=['POST'])  # ajax
@login_required
def observables_del_image():
    o = ObsClassroomImage.query.filter_by(obs_id=int(request.json['obs_id']),
                                          classroom_id=current_user.classroom_id).one()
    db.session.delete(o)
    db.session.commit()
    return 'ok'


@app.route('/observables/toggle_done', methods=['POST'])  # ajax
@login_required
def observables_toggle_done():
    try:
        o = ObsClassroomDone.query.filter_by(obs_id=int(request.json['obs_id']),
                                             classroom_id=current_user.classroom_id).one()
        db.session.delete(o)
        db.session.commit()
        return 'None'
    except NoResultFound:
        o = ObsClassroomDone(obs_id=int(request.json['obs_id']),
                             classroom_id=current_user.classroom_id)
        db.session.add(o)
        db.session.commit()
        return o.done.strftime('%d/%m/%Y')


@app.route('/observables/reset_done', methods=['POST'])  # ajax
@login_required
def observables_reset_done():
    o = ObsClassroomDone.query.filter_by(classroom_id=current_user.classroom_id).all()
    for d in o:
        db.session.delete(d)
    db.session.commit()
    return('reset_ok')


# __________________________________ENFANTS________________________________________________________
@app.route('/classe')
@login_required
def classroom():
    children = {}
    for child in Child.query.filter_by(classroom_id=current_user.classroom_id).all():
        if child.group() not in children.keys():
            children[child.group()] = [child]
        else:
            children[child.group()].append(child)
    return render_template('classroom.html', children=children)


@app.route('/classe/<grp>')  # ?field=id
@login_required
def group(grp):
    children = Child.query.filter_by(classroom_id=current_user.classroom_id).order_by(Child.birthdate)
    grps = set([c.group() for c in children])
    children = [c for c in children if c.group() == grp]
    cycle = Cycle.query.get(children[0].cycle())
    field_id = int(request.args.get('field')) if request.args.get('field') \
        else min([f.id for f in cycle.fields.values()])
    field = get_field(field_id, current_user.classroom.id)
    for c in children:
        c.field = get_field_child(c, field_id)
    return render_template('group.html', grps=grps, group=grp, cycle=cycle, field=field, children=children)

"""
@app.route('/validate', methods=['POST'])  # ajax
@login_required
def validate():
    child = Child.query.get(int(request.json['child_id']))
    obs_id = int(request.json['obs_id'])
    validated = request.json['validated']
    if not validated:
        image = ObsClassroomImage.query.filter_by(classroom_id=child.classroom_id, obs_id=obs_id).first()
        image = image.image if image else None
        oc = ObsChild(obs_id=obs_id, child_id=child.id, image=image, ability=0)
        db.session.add(oc)
        db.session.commit()
        return oc.date.strftime('%d/%m/%Y')

    elif validated:  # annuler
        o = ObsChild.query.filter_by(obs_id=int(request.json['obs_id']),
                                     child_id=child.id).one()
        db.session.delete(o)
        db.session.commit()
        age = child.age()
        level = Observable.query.get(obs_id).level
        if age == level:
            return 'next'
        elif age > level:
            return 'alert'
        elif level > age:
            return 'pass'
    return 'Erreur!'
"""

@app.route('/validate', methods=['POST'])  # ajax
@login_required
def validate():
    child = Child.query.get(int(request.json['child_id']))
    obs_id = int(request.json['obs_id'])
    validated = request.json['validated']

    try: # validated
        o = ObsChild.query.filter_by(obs_id=int(request.json['obs_id']), child_id=child.id).one()
        if o.ability == 4: # cancel validation : delete from database
            db.session.delete(o)
            db.session.commit()
            age = child.age()
            level = Observable.query.get(obs_id).level
            class_name = ''
            if age == level or level in [20, 50, 80]:
                class_name = 'next'
            elif age > level:
                class_name = 'required'
            elif level > age:
                class_name = 'pass'
            return json.dumps({'className': class_name})
        else:
            o.ability += 1
            o.date = datetime.datetime.now()
            db.session.commit()

    except NoResultFound: # not validated
        image = ObsClassroomImage.query.filter_by(classroom_id=child.classroom_id, obs_id=obs_id).first()
        image = image.image if image else None
        o = ObsChild(obs_id=obs_id, child_id=child.id, image=image, ability=0)
        db.session.add(o)
        db.session.commit()

    return json.dumps({'date': o.date.strftime('%d/%m/%Y'),
                       'className': {0: 'red', 1: 'orange', 2: 'blue', 3: 'lightgreen', 4: 'green'}[o.ability]})


@app.route('/enfant/observables/<int:child_id>')  # ?field=x
@login_required
def child_observables(child_id):
    child = Child.query.get(child_id)
    cycle = Cycle.query.get(child.cycle())
    field_id = int(request.args.get('field')) if request.args.get('field') \
        else min([f.id for f in cycle.fields.values()])
    field = get_field_child(child, field_id)
    return render_template('child-observables.html', cycle=cycle, child=child, field=field)


@app.route('/enfant_upload', methods=['POST'])  # ajax
@login_required
def child_upload():
    name = process_image(request.files.get('file'),
                         app.config['UPLOAD_OBS'])
    if name:
        if request.form.get('update') == 'false':
            img = ObsChild(obs_id=int(request.form.get('obs_id')),
                           child_id=int(request.form.get('child_id')),
                           image=name)
            db.session.add(img)
        else:
            print("no update")
            img = ObsChild.query.filter_by(obs_id=int(request.form.get('obs_id')),
                                           child_id=int(request.form.get('child_id'))).one()
            img.image = name
        db.session.commit()
        return name
    return "error"


@app.route('/enfant_del_image', methods=['POST'])  # ajax
@login_required
def child_del_image():
    child = Child.query.get(int(request.json['child_id']))
    obs_child = ObsChild.query.filter_by(obs_id=int(request.json['obs_id']),
                                         child_id=int(request.json['child_id'])).one()
    try:
        obs = ObsClassroomImage.query.filter_by(obs_id=int(request.json['obs_id']),
                                                classroom_id=child.classroom_id).one()
    except:
        obs = None
    obs_child.image = obs.image if obs else None
    print(obs_child.image)
    db.session.commit()
    return json.dumps({'image': obs_child.image})


@app.route('/enfant/bilan/<int:child_id>', methods=['GET', 'POST'])
@login_required
def child_summary(child_id):
    child = Child.query.get(child_id)
    if request.method == 'POST':
        simple = True if request.form.get('simple') else False
        warning = True if request.form.get('warning') else False
        next = True if request.form.get('next') else False
        transversal = True if request.form.get('transversal') else False
        cycle = Cycle.query.get(child.cycle())
        fields = [get_field_child(child, f.id) for f in cycle.fields.values()]
        filename = '%s_%s.pdf' % (child.lastname, child.firstname)
        # build_pdf(filename, child, fields, simple=simple, warning=warning, next=next, paths=app.config)
        build_pdf(filename, child, fields, simple=simple, paths=app.config)
        return send_file('%s%s' % (app.config['PDF'], filename))

    filename = "%s-%s-cycle" % (child.lastname, child.firstname)
    summaries = [f for f in os.listdir(app.config['PDF']) if f.find(filename) == 0]
    return render_template('child-summary.html', child=child, summaries=summaries)


@app.route('/enfant/commentaires/<int:child_id>', methods=['GET', 'POST'])
@login_required
def child_comments(child_id):
    child = Child.query.get(child_id)
    if request.method == 'POST':  # ajax
        if request.json['op'] == 'update':
            comment = Comment.query.get(int(request.json['comment_id']))
            comment.content = check_text(request.json['content'])
            db.session.commit()
            return json.dumps({'comment_id': comment.id})
        elif request.json['op'] == 'add':
            comment = Comment(child_id=child.id,
                              content=check_text(request.json['content']),
                              author=current_user.__repr__(),
                              grp=child.group(),
                              date=datetime.date.today())
            child.comments.append(comment)
            db.session.commit()
            return json.dumps({'comment_id': comment.id,
                               'content': comment.content,
                               'author': comment.author,
                               'group': comment.grp,
                               'date': comment.date.strftime("%d/%m/%Y")})
        elif request.json['op'] == 'del':
            comment = Comment.query.get(int(request.json['comment_id']))
            db.session.delete(comment)
            db.session.commit()
            return json.dumps({'comment_id': request.json['comment_id']})

    return render_template('child-comments.html', child=child)


@app.route('/rotate-image', methods=['POST'])  # ajax
@login_required
def rotation():
    path = '%s/%s' % (app.config['APPDIR'], request.json['image'])
    rotate_image(path)
    return request.json['image']


# __________________________________JOURNAL________________________________________________________
@app.route('/journal/tout', methods=['GET', 'POST'])
@login_required
def diary_all():
    if request.method == 'POST':
        diary_id = int(request.json['diary_id'])
        diary = Diary.query.get(diary_id)
        db.session.delete(diary)
        db.session.commit()
        os.remove('%s/%s' % (app.config['DIARY'], diary.filename))
        try:
            os.remove('%s/%s' % (app.config['PDF'], diary.filename.replace('json', 'pdf')))
        except FileNotFoundError:
            pass
        return json.dumps({'diary_id': diary_id})
    diaries = Diary.query.filter_by(classroom_id=current_user.classroom_id).order_by(Diary.date.desc()).all()
    return render_template('diary-all.html', diaries=diaries)


@app.route('/journal/prevoir/<day>')
@login_required
def diary_planning(day):
    children = Child.query.filter_by(classroom_id=current_user.classroom_id).all()

    try:
        tt = TimeTable.query.filter_by(classroom_id=current_user.classroom_id).one()
        with open('%s/%s' % (app.config['DIARY'], tt.filename), 'r') as f:
            tt = json.load(f)
            days = [day['name'] for day in tt]
            if day == 'n':
                return redirect(url_for('diary_planning', day=days[0]))

            # revoir
            if re.match(r'^d_[\d]+', day):
                with open('%s/%s' % (app.config['DIARY'], day), 'r') as f:
                    day = json.load(f)
                    day['date'] = datetime.date.fromtimestamp(day['date']).strftime('%d/%m/%Y')
            else:
                day = [d for d in tt if d['name'] == day][0]
                day['date'] = ''
                nb_lines = len(day['groups'][0]['items'])

    # no timetable
    except NoResultFound:
        return redirect(url_for('diary_timetable'))

    return render_template('diary-planning.html', days=days, day=day)


@app.route('/journal/save_week')
@login_required
def diary_week():
    try:
        tt = TimeTable.query.filter_by(classroom_id=current_user.classroom_id).one()
        with open('%s/%s' % (app.config['DIARY'], tt.filename), 'r') as f:
            tt = json.load(f)
            days = [day['name'] for day in tt]

    # no timetable
    except NoResultFound:
        return redirect(url_for('diary_timetable'))

    diaries = Diary.query.filter_by(classroom_id=current_user.classroom_id).order_by(Diary.date.desc()).all()
    return render_template('diary-all.html', diaries=diaries)


@app.route('/journal/save', methods=['POST'])
@login_required
def diary_save():
    d = int(request.json['day']['date'])
    d = datetime.date.fromtimestamp(d)
    try:
        diary = Diary.query.filter_by(classroom_id=current_user.classroom_id, date=d).one()
    except NoResultFound:
        filename = 'd_%d.json' % random.randint(0, 999999)
        diary = Diary(classroom_id=current_user.classroom_id,
                      filename=filename,
                      date=d)
        db.session.add(diary)
        db.session.commit()
    with open('%s/%s' % (app.config['DIARY'], diary.filename), 'w') as f:
        json.dump(request.json['day'], f, ensure_ascii=False, indent=4)

    if request.json['dest'] == 'pdf':
        date = '%s %s' % (request.json['day']['name'], d)
        filename = diary.filename.replace('json', 'pdf')
        build_diary('{}{}'.format(app.config['PDF'], filename), date, request.json['day'])
        return filename

    if request.json['dest'] == 'tasks':
        date = '%s %s' % (request.json['day']['name'], d)
        filename = 'essai.pdf'
        build_tasks('{}{}'.format(app.config['PDF'], filename), request.json['day'])
        return filename

    return '0'


@app.route('/journal/edt')
@login_required
def diary_timetable():
    groups = set()
    children = Child.query.filter_by(classroom_id=current_user.classroom_id)
    for c in children:
        groups.add(c.group())
    try:
        tt = TimeTable.query.filter_by(classroom_id=current_user.classroom_id).one()
        groups_tt = set()
        with open('%s/%s' % (app.config['DIARY'], tt.filename), 'r') as f:
            tt = json.load(f)
            for day in tt:
                for gr in day['groups']:
                    groups_tt.add(gr['name'])

        try:
            nb_lines = len(tt[0]['groups'][0]['items'])
        except IndexError:
            tt = []
            nb_lines = 0
        # Update tt
        if groups != groups_tt:
            if groups.intersection(groups_tt) == set():
                tt = []
            # Add to tt
            groups_to_add = groups.difference(groups_tt)
            for day in tt:
                group_proto = deepcopy(tt[0]['groups'][0])  # copy a cycle to keep the schedule
                for g in groups_to_add:
                    for item in group_proto['items']:
                        item['description'] = 'Une matière'
                        item['id'] = day['name'] + '_' + str(random.randint(0, 99999999999))
                        item['className'] = 'item ' + day['name']
                        item['color'] = '#f6b73c'
                    group_proto['name'] = g
                    day['groups'].append(group_proto)
            # Delete from tt
            groups_to_remove = groups_tt.difference(groups)
            if groups_to_remove != set():
                for day in tt:
                    day['groups'] = [g for g in day['groups'] if g['name'] not in groups_to_remove]

            flash('L\'emploi du temps à été mis à jour en fonction de la classe.')

    except NoResultFound:
        tt = []
        nb_lines = 0
    groups = sorted(groups, key=lambda g: age(g))
    return render_template('diary-timetable.html', tt=tt, groups=groups, nb_lines=nb_lines)


@app.route('/diary_timetable_save', methods=['POST'])  # ajax
@login_required
def diary_timetable_save():
    timetable = request.json['timetable']
    try:
        tt = TimeTable.query.filter_by(classroom_id=current_user.classroom_id).one()
    except NoResultFound:
        tt = TimeTable(classroom_id=current_user.classroom_id,
                       filename='tt_%s.json' % current_user.classroom_id)
        db.session.add(tt)
        db.session.commit()
    with open("%s/%s" % (app.config['DIARY'], tt.filename), "w") as f:
        json.dump(timetable, f, ensure_ascii=False, indent=4)
    return '0'


@app.route('/diary_timetable_pdf', methods=['POST'])
@login_required
def diary_timetable_pdf():
    filename = 'tt_%s.pdf' % current_user.classroom_id
    timetable = request.json['timetable']
    build_tt('%s%s' % (app.config['PDF'], filename), timetable)
    return filename


# __________________________________BLOG________________________________________________________
@app.route('/blog/articles', methods=['GET', 'POST'])
@login_required
def blog_articles():
    if request.method == 'POST':
        article = Article.query.get(int(request.json['article_id']))
        if request.json['op'] == 'del':
            db.session.delete(article)
        elif request.json['op'] == 'toggle_publication':
            article.is_published = not article.is_published
        elif request.json['op'] == 'toggle_edition':
            article.is_editable = not article.is_editable
        elif request.json['op'] == 'set_category':
            article.category_id = None if request.json['category'] == 'None' else int(request.json['category'])
            # result = db.session.execute('update article set category_id=%s where id=%s' % (request.json['category'], request.json['article_id']))
            # print(result)
        db.session.commit()
        return json.dumps({'article_id': request.json['article_id']})

    articles = Article.query.filter_by(classroom_id=current_user.classroom_id).order_by(Article.id.desc()).all()
    categories = Category.query.filter_by(classroom_id=current_user.classroom_id).order_by(Category.id.desc()).all()
    return render_template('blog-articles.html', articles=articles, categories=categories)


@app.route('/blog/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        if request.form.get('op') == 'add':
            cat = Category(classroom_id=current_user.classroom_id,
                           name=check_text(request.form.get('name')),
                           description=check_text(request.form.get('description')) if request.form.get(
                               'description') else None)
            db.session.add(cat)
        elif request.form.get('op') == 'del_category':
            category = Category.query.get(int(request.form.get('category_id')))
            db.session.delete(category)
            db.session.commit()
            return 'ok'
        elif request.form.get('op') == 'update_category':
            category = Category.query.get(int(request.form.get('category_id')))
            category.name = check_text(request.form.get('name'))
            category.description = check_text(request.form.get('description'))
        db.session.commit()
    categories = Category.query.filter_by(classroom_id=current_user.classroom_id).order_by(Category.id.desc()).all()
    return render_template('blog-categories.html', categories=categories)


@app.route('/blog/ecrire', methods=['GET', 'POST'])
@login_required
def blog_write():
    if request.method == 'POST':
        if request.json['op'] == 'add':
            article = Article(classroom_id=current_user.classroom_id,
                              title=check_text(request.json['title']),
                              content=check_text(request.json['content']),
                              image=request.json['image'])
            db.session.add(article)
        elif request.json['op'] == 'update':
            article = Article.query.get(int(request.json['article_id']))
            article.title = check_text(request.json['title'])
            article.content = check_text(request.json['content'])
            article.image = request.json['image']
        db.session.commit()
        return json.dumps({'article_id': article.id})

    article = request.args.get('article')
    if article == 'new':
        return render_template('blog-write.html', title='', content='', image=None)
    article = Article.query.get(int(article))
    return render_template('blog-write.html',
                           title=article.title,
                           content=article.content,
                           image=article.image)


@app.route('/blog/medias/<media_type>')
@login_required
def medias(media_type):
    files = []
    title = ''
    if media_type == 'img':
        files = BlogImage.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogImage.id.desc()).all()
        title = 'Images'
    elif media_type == 'audio':
        files = BlogAudio.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogAudio.id.desc()).all()
        title = 'Audio'
    elif media_type == 'video':
        files = BlogVideo.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogVideo.id.desc()).all()
        title = 'Vidéos'
    elif media_type == 'doc':
        files = BlogDoc.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogDoc.id.desc()).all()
        title = 'Documents'
    return render_template('blog-medias.html', title=title, media_type=media_type, files=files)


@app.route('/blog/media/add', methods=['POST'])  # ajax
@login_required
def media_add():
    file = request.files.get('file')
    media_type = request.form.get('media_type')
    if media_type == 'img':
        name = process_image(file, app.config['UPLOAD_BLOG_IMG'])
        if name:
            media = BlogImage(classroom_id=current_user.classroom_id,
                              filename=name)
    elif media_type == 'audio':
        media = BlogAudio(classroom_id=current_user.classroom_id,
                          filename=file.filename)
        file.save(os.path.join(app.config['UPLOAD_BLOG_AUDIO'], media.filename))
    elif media_type == 'video':
        media = BlogVideo(classroom_id=current_user.classroom_id,
                          filename=file.filename)
        file.save(os.path.join(app.config['UPLOAD_BLOG_VIDEO'], media.filename))
    elif media_type == 'doc':
        media = BlogDoc(classroom_id=current_user.classroom_id,
                        filename=file.filename)
        if file.content_type.find('opendocument.text') != -1 or file.content_type.find('word') != -1:
            media.preview = 'odt-file-5-504244.png'
        elif file.content_type.find('pdf') != -1:
            media.preview = 'iconepdf.png'
        file.save(os.path.join(app.config['UPLOAD_BLOG_DOC'], media.filename))
    db.session.add(media)
    db.session.commit()
    if media_type == 'doc':
        return json.dumps({'file_id': media.id, 'filename': media.filename, 'preview': media.preview})
    return json.dumps({'file_id': media.id, 'filename': media.filename})


@app.route('/blog/media/del', methods=['POST'])  # ajax
@login_required
def media_del():
    media_type = request.json['media_type']
    media_id = int(request.json['media_id'])
    if media_type == 'img':
        media = BlogImage.query.get(media_id)
    elif media_type == 'audio':
        media = BlogAudio.query.get(media_id)
    elif media_type == 'video':
        media = BlogVideo.query.get(media_id)
    elif media_type == 'doc':
        media = BlogDoc.query.get(media_id)
    db.session.delete(media)
    db.session.commit()
    return json.dumps({'media_id': media_id})


@app.route('/blog/add_media/<media_type>')
@login_required
def add_media(media_type):
    files = []
    title = ''
    if media_type == 'img' or media_type == 'main' or media_type == 'observables':
        files = BlogImage.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogImage.id.desc()).all()
        title = 'Images'
    elif media_type == 'audio':
        files = BlogAudio.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogAudio.id.desc()).all()
        title = 'Audio'
    elif media_type == 'video':
        files = BlogVideo.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogVideo.id.desc()).all()
        title = 'Vidéos'
    elif media_type == 'doc':
        files = BlogDoc.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogDoc.id.desc()).all()
        title = 'Documents'
    return render_template('blog-add-media.html', target=media_type, medias=files, title=title)


@app.route('/blog/stats')
@login_required
def statistiques():
    visits = BlogVisit.query.filter_by(classroom_id=current_user.classroom_id).order_by(BlogVisit.id.desc()).all()
    return render_template('blog-stats.html', visits=visits)


@app.route('/blog/visitors', methods=['GET', 'POST'])
@login_required
def visitors():
    return render_template('blog-visitors.html', visitors=Visitor.query.all())


@app.route('/blog/comments', methods=['GET', 'POST'])
@login_required
def blog_comments():
    if request.method == 'POST':
        if request.json['op'] == 'del':
            comment = ArticleComment.query.get(int(request.json['comment_id']))
            db.session.delete(comment)
            db.session.commit()
            return json.dumps({'comment_id': request.json['comment_id']})
        elif request.json['op'] == 'toggle_is_public':
            comment = ArticleComment.query.get(int(request.json['comment_id']))
            comment.is_public = not comment.is_public
            db.session.commit()
            return 'ok'
    articles = Article.query.filter_by(classroom_id=current_user.classroom_id).order_by(Article.id.desc()).all()
    print(articles)
    comments = []
    for article in articles:
        comments.extend(article.comments)
        print(article.title, article.comments)
    comments = sorted(comments, key=lambda com: com.datetime, reverse=True)
    return render_template('blog-comments.html', comments=comments)


@app.route('/blog-login/', methods=['GET', 'POST'])
def blog_login():
    if request.method == 'POST':
        visitor = Visitor.query.filter_by(email=request.form['email']).first()
        if not visitor or not visitor.check_password(request.form['password'] or not visitor.is_active):
            flash('Echec de l\'authentification')
            return render_template('blog-final-login.html', message='Echec de l\'authentification')
        session['visitor'] = visitor.id
        return redirect('/blog-ecole/')
    return render_template('blog-final-login.html', title='Connexion')


@app.route('/blog-lost-password/', methods=['GET', 'POST'])
def blog_lost_password():
    if request.method == 'POST':
        passwd = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
        msg = Message(subject='Mot de passe',
                      sender=app.config.get('MAIL_USERNAME'),
                      recipients=[request.form['email']],
                      body='Voici votre nouveau mot de passe: %s' % passwd)
        mail.send(msg)
        try:
            visitor = Visitor.query.filter_by(email=request.form['email']).first()
            visitor.set_password(passwd)
            db.session.commit()
            flash('Un nouveau mot de passe vous a été envoyé. Il est recommandé de le changer!')
            return redirect('/blog-login/')
        except AttributeError:
            flash('L\'adresse "%s" ne semble pas valide.' % request.form['email'])
    return render_template('blog-final-lost-password.html', title='Mot de passe oublié!')


@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        visitor = Visitor(firstname=request.form['firstname'],
                          lastname=request.form['lastname'],
                          email=request.form['email'])
        visitor.set_password(request.form['password'])
        try:
            db.session.add(visitor)
            db.session.commit()
            msg = Message(subject='Bienvenue!',
                          sender=app.config.get("MAIL_USERNAME"),
                          recipients=[visitor.email],  # replace with your email for testing
                          body='Confirmez votre inscription au blog de l\'école: \
                                https://suivisco.alwaysdata.net/blog-confirm/?u=%s' % visitor.id)
            mail.send(msg)
            flash('Il reste à confirmer l\'adresse. Un mail vous a été envoyé à cette fin.')
            return render_template('blog-final-register.html')
        except IntegrityError:  # email exists
            flash('Il y a un problème avec votre adresse!!')
        except:
            flash('Inscription réussie')
    return render_template('blog-final-register.html', title='Inscription')


@app.route('/blog-confirm/')
def confirm():
    visitor = Visitor.query.get(int(request.args.get('u')))
    visitor.is_active = True
    db.session.commit()
    return redirect('/blog-login/')


@app.route('/blog-logout/')
def blog_logout():
    del session['visitor']
    return redirect('/blog-ecole/')


@app.route('/myaccount/', methods=['GET', 'POST'])
def blog_account():
    visitor = Visitor.query.get(session['visitor'])
    if request.method == 'POST':
        if request.form.get('op') == 'update':
            if request.form.get('password') == request.form.get('password2'):
                visitor.set_password(request.form.get('password'))
                flash('Votre mot de passe a été mis à jour.')
            else:
                flash('Il y a une erreur sur le mot de passe.')
        elif request.form.get('op') == 'delete':
            post = ArticleComment.query.get(int(request.form.get('comment_id')))
            db.session.delete(post)
        elif request.form.get('op') == 'delete_visitor':
            db.session.delete(visitor)
            db.session.commit()
            del session['visitor']
            return redirect('/blog-ecole/')
        db.session.commit()
    posts = ArticleComment.query.filter_by(visitor_id=visitor.id).order_by(ArticleComment.id.desc()).all()

    return render_template('blog-final-account.html', posts=posts, visitor=visitor, title='Mon compte')


# stats
def stats(classroom_id=None):
    if current_user.is_anonymous:
        try:
            visitor_id = session['visitor_id']
        except KeyError:
            session['visitor_id'] = random.randint(0, 999999999)
        previous_visit = BlogVisit.query.filter_by(visitor_id=session['visitor_id']).order_by(
            BlogVisit.id.desc()).first()
        if not previous_visit or datetime.datetime.now() - previous_visit.datetime > datetime.timedelta(minutes=2):
            visit = BlogVisit(visitor_id=session['visitor_id'],
                              remote_addr=request.remote_addr,
                              classroom_id=classroom_id)
            db.session.add(visit)
            db.session.commit()


def accept_cookies():
    if session.get('accept_cookies') is None:
        session['accept_cookies'] = False
    return session['accept_cookies']


@app.route('/accept_cookies', methods=['POST'])
def rgpd():
    session['accept_cookies'] = True
    return 'ok'


@app.route('/blog-ecole/visio', methods=['GET', 'POST'])
def blog_visio():
    try:
        visitor = session['visitor']
        visitor = Visitor.query.get(int(visitor))
    except KeyError:
        visitor = None
    if not visitor and not current_user.is_authenticated:
        return render_template('blog-final-login.html', title='Connexion', a_c=True)

    visio_session = BlogVisio.query.get(1)
    # première requête seulement
    if visio_session is None:
        visio_session = BlogVisio(is_available=False, ref=1)
        db.session.add(visio_session)
        db.session.commit()

    if request.method == 'POST':
        if current_user.is_authenticated and request.json['op'] == 'begin':
            visio_session.is_available = True
            visio_session.ref = random.randint(0, 99999)
            db.session.commit()
            o = True
        elif current_user.is_authenticated and request.json['op'] == 'stop':
            visio_session.is_available = False
            visio_session.ref = random.randint(0, 99999)
            db.session.commit()
            o = True
        return json.dumps({'status': visio_session.is_available, 'ref': visio_session.ref})

    classroom_id = 1
    cls = ClassRoom.query.get(classroom_id)
    return render_template('blog-final-visio.html', status= visio_session.is_available, visitor=visitor,
                           ref=visio_session.ref, title='Visio')


@app.route('/blog-ecole/random/<mode>')
def blog_random(mode):
    children = {}
    c = Child.query.filter_by(classroom_id=current_user.classroom_id).all()
    for child in c:
        if child.group() not in children.keys():
            children[child.group()] = [child]
        else:
            children[child.group()].append(child)
    print(children)
    template = 'blog-final-random-one.html' if mode == 'one' else 'blog-final-random-team.html'
    return render_template(template, children=children, number=math.floor(len(c)/2), title='Hasard')


@app.route('/blog-ecole/ceb')
def blog_ceb():
    return render_template('blog-final-ceb.html',  title='Le compte est bon!')



@app.route('/blog-ecole/', methods=['GET', 'POST'])
def blog_ecole():
    classroom_id = 1
    cls = ClassRoom.query.get(classroom_id)

    try:
        visitor = session['visitor']
        visitor = Visitor.query.get(int(visitor))
    except KeyError:
        visitor = None

    # menu principal
    if request.method == 'GET' and len(request.args) == 0:
        stats(classroom_id)
        cats = Category.query.all()
        articles = [Article.query.filter_by(classroom_id=classroom_id, is_published=True, category_id=c.id).order_by(
            Article.id.desc()).first() for c in cats]
        articles.append(
            Article.query.filter_by(classroom_id=classroom_id, is_published=True, category_id=None).order_by(
                Article.id.desc()).first())
        articles = [a for a in articles if a]
        if articles is True:
            articles = sorted(articles, key=lambda art: art.id, reverse=True)
            first = [a for a in articles if a.category and a.category.name == 'Informations'][0]
            first = articles.pop(articles.index(first))
            articles = [first] + articles
        for a in articles:
            a.content = re.sub('<[^<]+?>', '', a.content)[:100] + '[...]'
        return render_template('blog-final-home.html', articles=articles, title='La classe des %s' % cls.name,
                               visitor=visitor, a_c=True)

    # demande de plus d'articles
    if request.method == 'POST':
        a_json = dict()
        category_id = None if request.json['category_id'] == 'None' else int(request.json['category_id'])
        articles = Article.query.filter_by(classroom_id=classroom_id, is_published=True,
                                           category_id=category_id).order_by(Article.id.desc()) \
            .limit(4).offset(int(request.json['offset'])).all()
        if not articles:
            a_json['articles'] = []
            return json.dumps(a_json)
        a = Article.query.filter_by(classroom_id=classroom_id, is_published=True, category_id=category_id).limit(
            4).offset(int(request.json['offset'] + 4)).all()
        a_json['next'] = True if a else False
        articles_json = []
        print(articles)
        for article in articles:
            a = {'title': article.title, 'content': article.content, 'article_id': article.id,
                 'date': article.date.strftime("%d/%m/%Y"), 'image': article.image, 'is_editable': article.is_editable}
            a['comments'] = []
            if visitor or current_user.is_authenticated:
                for com in article.comments:
                    # ne pas ajouter les commentaires privés si..
                    if not com.is_public and not current_user.is_authenticated and not (
                            visitor and visitor.id == com.visitor_id):
                        continue
                    if com.is_public or current_user.is_authenticated or (visitor and visitor.id == com.visitor_id):
                        content = com.content.replace('#!', '<').replace('&?', '>').replace('?%', ';')
                        # indiquer si l'emetteur de la requête est propriétaire du commentaire
                        owner = True if (visitor and visitor.id == com.visitor_id) or (
                                    current_user.is_authenticated and current_user.id == com.user_id) else False
                        a['comments'].append({'id': com.id, 'author': com.author, 'article_id': com.article_id,
                                              'is_public': com.is_public,
                                              'content': content, 'date': com.datetime.strftime("%d/%m/%Y"),
                                              'owner': owner})
            articles_json.append(a)

        a_json['articles'] = articles_json
        return json.dumps(a_json)

    # dans une catégorie
    category_id = None if request.args.get('cat') == 'None' else int(request.args.get('cat'))
    articles = Article.query.filter_by(classroom_id=classroom_id, is_published=True, category_id=category_id).order_by(
        Article.id.desc()).limit(4).all()
    next = True if Article.query.filter_by(classroom_id=classroom_id, is_published=True, category_id=category_id).limit(
        1).offset(4).all() else False

    resp = make_response(render_template('blog-final-articles.html', title='La classe des %s' % cls.name,
                                         articles=articles, next=next, visitor=visitor))
    return resp


@app.route('/add-media-comment/', methods=['POST'])  # ajax
def add_media_comment():
    file = request.files.get('file')
    filename = file.filename.replace(' ', '')
    preview = None
    if file.content_type.find('audio') != -1:
        content_type = 'audio'
        file.save(os.path.join(app.config['UPLOAD_VISITOR_DATA'], secure_filename(filename)))
    elif file.content_type.find('image') != -1:
        content_type = 'img'
        filename = process_image(file, app.config['UPLOAD_VISITOR_DATA'])
    elif file.content_type.find('video') != -1:
        content_type = 'video'
        file.save(os.path.join(app.config['UPLOAD_VISITOR_DATA'], secure_filename(filename)))
    elif file.content_type.find('opendocument.text') != -1 or file.content_type.find('word') != -1:
        preview = 'odt-file-5-504244.png'
        content_type = 'doc'
        file.save(os.path.join(app.config['UPLOAD_VISITOR_DATA'], secure_filename(filename)))
    elif file.content_type.find('pdf') != -1:
        preview = 'iconepdf.png'
        content_type = 'doc'
        file.save(os.path.join(app.config['UPLOAD_VISITOR_DATA'], secure_filename(filename)))
    else:
        content_type = 'invalid file'
    print(request.form)
    article_id = int(request.form.get('article_id'))
    return json.dumps({'article_id': article_id, 'content_type': content_type, 'filename': filename, 'preview': preview})


@app.route('/articles-comments/', methods=['POST'])
def articles_comments():  # ajax
    if request.json['op'] == 'add':
        data = request.json
        print(data)
        visitor_id = int(data['user_id']) if data['is_visitor'] == 'True' else None
        user_id = int(data['user_id']) if data['is_visitor'] == 'False' else None
        text = check_text(data['text']).replace('<', '#!').replace('>', '&?').replace(';', '?%').replace('<script>', '')

        comment = ArticleComment(article_id=data['article_id'],
                                 visitor_id=visitor_id,
                                 user_id=user_id,
                                 author=data['author'],
                                 content=text,
                                 is_public=data['is_public'])
        db.session.add(comment)
        db.session.commit()
        print(comment.__dict__)
        return json.dumps({'article_id': comment.article_id,
                           'author': comment.author,
                           'date': comment.datetime.strftime("%d/%m/%Y"),
                           'content': data['text'],
                           'comment_id': comment.id,
                           'is_public': comment.is_public})

    elif request.json['op'] == 'del':
        comment = ArticleComment.query.get(int(request.json['comment_id']))
        db.session.delete(comment)
        db.session.commit()
        return json.dumps({'comment_id': request.json['comment_id']})

    elif request.json['op'] == 'toggle_is_public':
        comment = ArticleComment.query.get(int(request.json['comment_id']))
        comment.is_public = not comment.is_public
        db.session.commit()
    return 'ok'


@app.route('/articles-comments-answer/', methods=['POST'])
def articles_comments_answer():  # ajax
    if request.json['op'] == 'add':
        data = request.json
        print("on set là ", data)
        visitor_id = int(data['user_id']) if data['is_visitor'] == 'True' else None
        user_id = int(data['user_id']) if data['is_visitor'] == 'False' else None
        text = check_text(data['text']).replace('<', '#!').replace('>', '&?').replace(';', '?%').replace('<script>', '')

        answer = ArticleCommentAnswer(article_comment_id=data['comment_id'],
                                 visitor_id=visitor_id,
                                 user_id=user_id,
                                 author=data['author'],
                                 content=text)
        db.session.add(answer)
        db.session.commit()
        print(answer.__dict__)
        return json.dumps({'article_comment_id': answer.article_comment_id,
                           'author': answer.author,
                           'date': answer.datetime.strftime("%d/%m/%Y"),
                           'content': data['text'],
                           'answer_id': answer.id})

    elif request.json['op'] == 'del':
        answer = ArticleCommentAnswer.query.get(int(request.json['answer_id']))
        db.session.delete(answer)
        db.session.commit()
        return json.dumps({'answer_id': request.json['answer_id']})

    return 'ok'


@app.route('/mentions_legales/')
def mentions_legales():
    return render_template('blog-final-mentions.html', title='Mentions légales', mentions=False)



# __________________________________ADMIN________________________________________________________
def is_staff_required(fn):
    def check(**kwargs):
        if current_user.is_staff:
            return fn(**kwargs)
        else:
            abort(403)

    # truc bizarre lié à l'enchaiemenrnt avec app.route:
    # https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
    check.__name__ = fn.__name__
    return check


@app.route('/admin/')
@is_staff_required
def admin_redirect():
    return redirect("/admin/observables?cycle=1&field=1")


@app.route('/admin/observables')  # url?cycle=1&field=1
@is_staff_required
def admin_observables():
    cycle_id = int(request.args.get('cycle')) if request.args.get('cycle') else 1
    cycle = Cycle.query.get(cycle_id)

    field_id = int(request.args.get('field')) if request.args.get('field') \
        else min([f.id for f in cycle.fields.values()])
    #f = Field.query.get(field_id)
    f = get_field(field_id, current_user.classroom.id)
    return render_template('admin-observables.html',
                           cycle=cycle,
                           field=f)


@app.route('/admin_observables_pdf', methods=['POST', 'GET'])
@login_required
def admin_observables_pdf():
    cycle_id = int(request.json['cycle_id'])
    c = Cycle.query.get(cycle_id)
    fields = [get_field(f.id, current_user.classroom.id)  for f  in c.fields.values()]
    filename = 'observables_cycle_%d.pdf' % cycle_id
    build_obs_table('%s%s' % (app.config['PDF'], filename), fields, c)
    return filename


@app.route('/editor')
@is_staff_required
def obs_editor():
    op = request.args.get('op')
    obj_type = request.args.get('type')
    obj_id = int(request.args.get('id'))
    content = ''
    title = ''
    if obj_type == 'field':
        content = Field.query.get(obj_id).name
        title = 'Ajouter une competence au domaine'
    elif obj_type == 'skill':
        content = Skill.query.get(obj_id).name
        if op == 'update':
            title = 'Modifier le texte d\'une compétence'
        elif op == 'add':
            title = 'Ajouter un observable à la compétence'
    elif obj_type == 'obs':
        title = 'Modifier le texte d\'un observable'
        content = Observable.query.get(obj_id).name
    return render_template("admin-edit.html", title=title, content=content, update=op)


@app.route('/add_skill', methods=['POST'])  # ajax
@is_staff_required
def add_skill():
    data = request.json
    position = len(Field.query.get(int(data['id'])).skills.keys()) + 1
    new_skill = Skill(name=check_text(data['name']),
                      position=position,
                      field_id=data['id'])
    db.session.add(new_skill)
    db.session.commit()
    return json.dumps({'name': new_skill.name, 'id': new_skill.id, 'position': new_skill.position})


@app.route('/add_obs', methods=['POST'])  # ajax
@is_staff_required
def add_obs():
    data = request.json
    s = Skill.query.get(int(data['id']))
    position = len(s.observables.keys()) + 1
    cycle_id = Cycle.query.get(Field.query.get(s.field_id).cycle_id).id
    if cycle_id == 1:
        level = 0
    elif cycle_id == 2:
        level = 3
    else:
        level = 6
    new_obs = Observable(name=check_text(data['name']),
                         position=position,
                         skill_id=data['id'], level=level)
    db.session.add(new_obs)
    db.session.commit()
    return json.dumps({'name': new_obs.name, 'id': new_obs.id,
                       'position': new_obs.position, 'skill_id': new_obs.skill_id})


@app.route('/move_skill', methods=['POST'])  # ajax
@is_staff_required
def move_skill():
    up = Skill.query.get(int(request.json['up']))
    down = Skill.query.get(int(request.json['down']))
    up.position -= 1
    down.position += 1
    db.session.commit()
    up = '%d. %s' % (up.position, up.name)
    down = '%d. %s' % (down.position, down.name)
    return json.dumps({'up': up, 'down': down})


@app.route('/move_obs', methods=['POST'])  # ajax
@is_staff_required
def move_obs():
    up = Observable.query.get(int(request.json['up']))
    down = Observable.query.get(int(request.json['down']))
    up.position -= 1
    down.position += 1
    db.session.commit()
    up = '%d. %s' % (up.position, up.name)
    down = '%d. %s' % (down.position, down.name)
    return json.dumps({'up': up, 'down': down})


@app.route('/del_skill', methods=['POST'])  # ajax
@is_staff_required
def del_skill():
    print(request.json['skill_id'] )
    skill = Skill.query.get(request.json['skill_id'])
    field = Field.query.get(skill.field_id)
    json_dict = {'skill_id': request.json['skill_id']}
    for s in field.skills.values():
        if s.position > skill.position:
            s.position -= 1
            json_dict[s.id] = '%d. %s' % (s.position, s.name)
    db.session.delete(skill)
    db.session.commit()
    return json.dumps(json_dict)


@app.route('/del_obs', methods=['POST'])  # ajax
@is_staff_required
def del_obs():
    obs = Observable.query.get(int(request.json['obs_id']))
    skill = Skill.query.get(obs.skill_id)
    json_dict = {'obs_id': request.json['obs_id']}
    for o in skill.observables.values():
        if o.position > obs.position:
            o.position -= 1
            json_dict[o.id] = '%d. %s' % (o.position, o.name)
    db.session.delete(obs)
    db.session.commit()
    return json.dumps(json_dict)


@app.route('/update_name', methods=['POST'])  # ajax
@is_staff_required
def update_name():
    data = request.json
    item = None
    if data['item_type'] == 'skill':
        item = Skill.query.get(int(data['id']))
    if data['item_type'] == 'obs':
        item = Observable.query.get(int(data['id']))
    item.name = check_text(data['name'])
    db.session.commit()
    return json.dumps({'id': item.id, 'position': item.position, 'name': item.name})


@app.route('/update_level', methods=['POST'])  # ajax
@is_staff_required
def update_level():
    obs = Observable.query.get(request.json['obs_id'])
    # ne pas dépasser le niveau possible dans un cycle! Retour au début du cycle si dépassement.
    # cycle 1: 0, 1, 2; cycle 2: 3, 4, 5; cycle 3: 6, 7, 8
    # transcycle : level*10
    if obs.level in [2, 5, 8]:
        obs.level *= 10
    elif obs.level in [20, 50, 80]:
        obs.level /= 10
        obs.level -= 2
    else:
        obs.level += 1
    db.session.commit()
    #return str(obs.level)
    return json.dumps({'level': obs.level, 'levelstr': {0: 'PS', 1: 'MS', 2: 'GS', 3: 'CP',
                4: 'CE1', 5: 'CE2', 6: 'CM1', 7: 'CM2', 8:'6ème', 20: 'tous', 50: 'tous', 80: 'tous'}[obs.level]})


@app.route('/admin/classes', methods=['GET', 'POST'])
@is_staff_required
def classrooms():
    if request.method == 'POST':
        print(request.form)
        if request.form.get('op') == 'add_child':
            d, m, y = request.form['birthdate'].split('/')
            birthdate = datetime.date(int(y), int(m), int(d))
            child = Child(firstname=request.form['firstname'],
                          lastname=request.form['lastname'],
                          gender=request.form['gender'],
                          birthdate=birthdate)
            db.session.add(child)
        elif request.form.get('op') == 'update_child':
            d, m, y = request.form['birthdate'].split('/')
            birthdate = datetime.date(int(y), int(m), int(d))
            child = Child.query.get(int(request.form['id']))
            child.birthdate = birthdate
            child.firstname = request.form['firstname']
            child.lastname = request.form['lastname']
            child.gender = request.form['gender']
            child.speed = request.form['speed']
        elif request.form.get('op') == 'delete_child':
            child = Child.query.get(int(request.form['child_id']))
            db.session.delete(child)
        elif request.form.get('op') == 'add_classroom':
            class_room = ClassRoom(name=request.form['name'])
            db.session.add(class_room)
        elif request.form.get('op') == 'update_classroom':
            class_room = ClassRoom.query.get(int(request.form['classroom_id']))
            class_room.name = request.form['name']
        elif request.form.get('op') == 'delete_classroom':
            class_room = ClassRoom.query.get(int(request.form['classroom_id']))
            db.session.delete(class_room)
        db.session.commit()

    children = Child.query.order_by(Child.birthdate.desc())
    class_rooms = ClassRoom.query.all()
    return render_template('admin-classrooms.html',
                           children=children,
                           classrooms=class_rooms)


@app.route('/get_child', methods=['POST'])  # ajax
@is_staff_required
def get_child():
    child = Child.query.get(int(request.json['child_id']))
    child.birthdate = child.birthdate.strftime("%d/%m/%Y")
    return json.dumps({'id': child.id,
                       'firstname': child.firstname,
                       'lastname': child.lastname,
                       'birthdate': child.birthdate,
                       'gender': child.gender,
                       'speed': child.speed})


@app.route('/update_classroom', methods=['POST'])  # ajax
@is_staff_required
def update_child_classroom():
    class_id = int(request.json['class_id']) if request.json['class_id'] != '' else None
    child_id = int(request.json['child_id'])
    c = Child.query.get(child_id)
    c.classroom_id = class_id
    db.session.commit()
    return 'ok'


@app.route('/admin/users', methods=['GET', 'POST'])
@is_staff_required
def users():
    if request.method == 'POST':
        try:
            passwd = ''.join([random.choice(string.ascii_letters) for _ in range(6)])
            msg = Message(subject='Bienvenue sur suivisco.alwaydata.net',
                          sender=app.config.get('MAIL_USERNAME'),
                          recipients=[request.form['email']],
                          body="Bonjour! \
                               Vous avez été(e) inscrit(e) sur suivisco.alwaysdata.net \
                               Pour vous connecter: \
                               login: %s ,\
                               mot de passe: %s \
                               Il est recommandé de changer le mot de passe!" % (request.form['email'], passwd))
            mail.send(msg)

            user = User(firstname=request.form['firstname'],
                        lastname=request.form['lastname'],
                        email=request.form['email'])
            user.set_password(passwd)
            db.session.add(user)
            db.session.commit()
        except AttributeError:
            flash('L\'adresse "%s" ne semble pas valide.' % request.form['email'])
        except:
            flash('Le mail n\'a pas pu être envoyé. L\'inscription a échouée')


    return render_template('admin-users.html', users=User.query.all(), classrooms=ClassRoom.query.all())


@app.route('/update_user_classroom', methods=['POST'])  # ajax
@is_staff_required
def update_user_classroom():
    u = User.query.get(int(request.json['user_id']))
    try:
        u.classroom_id = int(request.json['classroom_id'])
    except ValueError:
        u.classroom_id = None
    db.session.commit()
    return 'ok'


@app.route('/update_user_is_staff', methods=['POST'])  # ajax
@is_staff_required
def update_user_is_staff():
    u = User.query.get(int(request.json['user_id']))
    u.is_staff = not u.is_staff
    db.session.commit()
    print(u.is_staff)
    return 'ok'


@app.route('/del_user', methods=['POST'])  # ajax
@is_staff_required
def del_user():
    u = User.query.get(int(request.json['user_id']))
    db.session.delete(u)
    db.session.commit()
    return 'ok'

"""
@route("/admin/archivage", method=["GET", "POST"])
@is_staff_required
def archives(user=None):
    if request.method == "POST":
        if request.forms.journal == "ok":
            path = "data/"
            for file in os.listdir(path):
                if not re.match("edt", file):
                    os.remove("%s%s" % (path, file))
            path= "static/journal/"
            for file in os.listdir(path):
                os.remove("%s%s" % (path, file))

        if request.forms.archivage == "ok":
            enfants = [e for e in EnfantManager().get_enfants(user)
                       if e.groupe=="GS"
                       or e.groupe=="CE2"
                       or e.groupe=="CM2"]
            for enfant in enfants:
                filename = '%s_%s.pdf' % (enfant.nom, enfant.prenom)
                path = 'static/pdf/'
                try:
                    os.remove("%s/%s" % (path, filename))
                except FileNotFoundError:
                    pass
                enfant = EnfantManager().get_enfant(enfant.id, user.id) # pour ajouter les commentaires
                # gestion des pdf
                domaines = DomaineManager().get_cycle(groupe_cycle(enfant.groupe)).domaines.values()
                obs = []
                for domaine in domaines:
                    if domaine.nom == "Compétences transversales":
                        continue
                    obs.append(EnfantManager().get_domaine_enfant(enfant, domaine.id, user.id))
                filename = 'static/pdf/%s-%s-cycle-%s.pdf' % (enfant.nom, enfant.prenom, groupe_cycle(enfant.groupe))
                build_pdf(filename, enfant, obs, simple=False, warning=False, suite=False)
                # Supprimer les entrées de la table obs_enfants
                EnfantManager().annule_tout_enfant(enfant.id)

        if request.forms.images == "ok":
            images = EnfantManager().get_images()
            [images.append(im) for im in DomaineManager().get_images() if im not in images]
            images2 = os.listdir("static/images/observables")
            print(images2)
            for im in images2:
                if im not in images:
                    os.remove("static/images/observables/%s" % im)

    return template("admin/archives.tpl", user=user)
"""
