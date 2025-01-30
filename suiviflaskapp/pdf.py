import copy
from datetime import datetime

from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    PageBreak,
    FrameBreak,
    Image,
    KeepTogether,
    Table,
    TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from .pdfstyle import *
from datetime import datetime
from .utils import school_year


def im(path, doc):
    width = doc.width / 2 - doc.leftMargin / 2
    with open(path, 'rb') as image:  # l'image est fermée à la fin.
        im1 = Image(image)
        if im1.imageWidth == im1.imageHeight:
            height = width
        elif im1.imageWidth > im1.imageHeight:
            ratio = im1.imageWidth / im1.imageHeight
            height = width / ratio
        else:
            ratio = im1.imageHeight / im1.imageWidth
            height = width * ratio
    return Image(path, width=width, height=height)


# def build_pdf(filename, child, observables, simple=True, warning=True, next=True, paths=None):
def build_pdf(filename, child, observables, simple=True, paths=None):
    """Construction du pdf."""
    # Ajouter:
    # les compétences de l'année en cours -> simple = False
    # les compétences de tout le cycle -> simple = True
    doc = BaseDocTemplate('%s%s' % (paths['PDF'], filename),
                          leftMargin=1 * cm,
                          rightMargin=1 * cm,
                          topMargin=1 * cm,
                          bottomMargin=1 * cm,
                          title=child.__str__(), )
    column_gap = 0.5 * cm
    doc.addPageTemplates(
        [
            PageTemplate(
                frames=[
                    Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height,
                        id='left',
                        # rightPadding=column_gap / 2,
                        showBoundary=0  # set to 1 for debugging
                    ),
                    Frame(
                        doc.leftMargin + doc.width / 2,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height,
                        id='right',
                        # leftPadding=column_gap / 2,
                        showBoundary=0
                    ),
                ]
            ),
        ]
    )

    flowables = list()

    # Page de garde
    flowables.append(Paragraph('Livret de suivi des apprentissages', stylesheet()['garde']), )
    flowables.append(Spacer(0, cm * 0.5))
    date = datetime.today()
    flowables.append(Paragraph('Édité le %s' % date.strftime("%d/%m/%Y"), stylesheet()['default']), )
    flowables.append(Spacer(0, cm * 22))
    flowables.append(Paragraph('École Rachel Taytel', stylesheet()['dom']), )
    flowables.append(Spacer(0, cm * 0.5))
    flowables.append(Paragraph('33710 Teuillac', stylesheet()['dom']), )
    flowables.append(FrameBreak())

    string = '%s\n(%s)' % (child.__str__(), child.birthdate.strftime("%d/%m/%Y"))
    flowables.append(Paragraph(string, stylesheet()['nom']), )
    flowables.append(Spacer(0, cm * 24))
    flowables.append(PageBreak())

    # Suite
    for field in observables:
        # Ne pas ajouter un domaine vide!
        empty = True
        for index in sorted(field.skills.keys()):
            skill = field.skills[index]
            for index2 in sorted(skill.observables.keys()):
                observable = skill.observables[index2]
                if observable.date is None:
                    continue
                if simple is True and observable.age > observable.level:
                    continue
                empty = False
        if empty is True:
            continue

        #flowables.append(PageBreak())
        flowables.append(Paragraph('<b>%s</b>' % field.name, stylesheet()['dom']), )
        flowables.append(Spacer(0, cm * .3))

        for index in sorted(field.skills.keys()):
            skill = field.skills[index]
            # len_comp = len(competence.observables)
            first = [Paragraph('<b>%s</b>' % skill.name, ParagraphStyle('comp')), Spacer(0, cm * .3)]
            first_obs = True
            for index2 in sorted(skill.observables.keys()):
                observable = skill.observables[index2]
                if observable.date is None:
                    continue
                elif simple is True and (observable.age > observable.level or school_year(observable.date) != school_year(datetime.today())):
                    continue

                #obs = Paragraph('→ %s' % observable.name, stylesheet()[observable.status_s])
                #obs = Paragraph('<font color="%s">→</font> %s' % (observable.status_s, observable.name), stylesheet()['default'])

                pos = [
                    '<font color="lightgrey">⬛</font>',
                    '<font color="lightgrey">⬛</font>',
                    '<font color="lightgrey">⬛</font>',
                    '<font color="lightgrey">⬛</font>',
                    '<font color="lightgrey">⬛</font>',
                    ]
                pos[observable.status] = '<font color="%s">⬛</font>' % observable.status_s
                pos = ''.join(pos)
                obs = Paragraph('%s %s' % (observable.name, pos), stylesheet()['default'])
                ajout = obs
                #if observable.position == 1:
                if first_obs is True:
                    if observable.image_child is not None:
                        path = '%s%s' % (paths['UPLOAD_OBS'], observable.image_child)
                        obs = [obs, im(path, doc)]
                    else:
                        obs = [obs]
                    ajout = KeepTogether(first + obs)
                    first_obs = False
                else:
                    if observable.image_child is not None:
                        path = '%s%s' % (paths['UPLOAD_OBS'], observable.image_child)
                        ajout = KeepTogether([obs, im(path, doc)])

                """
                if path is not None and observable.status == 0:
                    if simple is True or observable.position == 1:
                        ajout = KeepTogether(first + [obs, im(path, doc)])
                    else:
                        ajout = KeepTogether([obs, im(path, doc)])
                else:
                    if warning is True and observable.status == 1 and observable.position != 1:
                        ajout = obs
                    elif simple is True or observable.position == 1:
                        ajout = KeepTogether(first + [obs])
                    else:
                        ajout = obs
                """

                flowables.append(ajout)
                flowables.append(Spacer(0, cm * .3))
                first_obs = False

                """
                # Ajouter la perspective
                if next is True \
                        and index2 + 1 in skill.observables.keys() \
                        and observable.status != 1:
                    observable2 = skill.observables[index2 + 1]
                    if warning is True and observable2.status == 1:
                        pass
                    elif observable2.status != 0:
                        obs = Paragraph('%s' % observable2.name, stylesheet()['suite'])
                        flowables.append(obs)
                        flowables.append(Spacer(0, cm * .3))
                """

    # Commentaires
    flowables.append(PageBreak())
    flowables.append(Paragraph('<b>Observations</b>', stylesheet()['dom']), )
    flowables.append(Spacer(0, cm * .3))
    current_groupe = None
    for commentaire in child.comments:
        if commentaire.grp != child.group() and simple is True:
            continue
        if commentaire.grp != current_groupe:
            current_groupe = commentaire.grp
            flowables.append(Paragraph(commentaire.grp, stylesheet()['comp']), )
            flowables.append(Spacer(0, cm * .3))

        # traitement balises html
        text = commentaire.content.replace('<div>', '<br/>').replace('</div>', '').replace('<br>', '<br/')
        flowables.append(Paragraph(text, stylesheet()['default']), )
        flowables.append(Spacer(0, cm * .1))
        context = '%s (le %s)' % (commentaire.author, commentaire.date.strftime("%d/%m/%Y"))
        flowables.append(Paragraph(context, stylesheet()['default']), )
        flowables.append(Spacer(0, cm * .3))
    doc.build(flowables)


def build_obs_table(filename, fields, c):
    doc = BaseDocTemplate(filename,
                          leftMargin=1 * cm,
                          rightMargin=1 * cm,
                          topMargin=1 * cm,
                          bottomMargin=1 * cm,
                          title=filename,)
    doc.addPageTemplates(
        [
            PageTemplate(
                frames=[
                    Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        showBoundary=0  # set to 1 for debugging
                    ),
                ],
            ),
        ]
    )
    flowables = list()

    # Page de garde
    flowables.append(Paragraph('Progressions cycle %d' % c.id, stylesheet()['garde']), )
    flowables.append(Spacer(0, cm * 0.5))
    date = datetime.today()
    flowables.append(Paragraph('Édité le %s' % date.strftime("%d/%m/%Y"), stylesheet()['default']), )
    flowables.append(Spacer(0, cm * 22))
    flowables.append(Paragraph('École Rachel Taytel', stylesheet()['dom']), )
    flowables.append(Spacer(0, cm * 0.5))
    flowables.append(Paragraph('33710 Teuillac', stylesheet()['dom']), )

    #récuperer les niveaux de classe du cycle
    levels = list()
    for field in fields:
        for skill in field.skills.values():
            for observable in skill.observables.values():
                if observable.level % 10 == 0 and observable.level != 0: continue
                o = (observable.level, observable.levelstr)
                if o not in levels: levels.append(o)
    print(sorted(levels, key=lambda a : a[0]))

    for field in fields:
        flowables.append(PageBreak())
        flowables.append(Paragraph('<b>%s</b>' % field.name, stylesheet()['dom']), )

        table = []
        t_style = [
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]

        line_number = 0
        for index in sorted(field.skills.keys()):
            line = list()
            skill = field.skills[index]
            line.append(Paragraph('<b>%s</b>' % skill.name, ParagraphStyle('comp')))
            for l in sorted(levels, key=lambda a : a[0]):
                line.append(Paragraph('<b>%s</b>' % l[1], ParagraphStyle('comp')))
            table.append(line)
            t_style.append(('BACKGROUND',(0, line_number),(4, line_number),colors.lightgrey))
            line_number += 1

            for index2 in sorted(skill.observables.keys()):
                line = list()
                obs = Paragraph(skill.observables[index2].name, stylesheet()['default'])
                line.append(obs)
                for l in sorted(levels, key=lambda a : a[0]):
                    if skill.observables[index2].level == l[0]:
                        line.append('X')
                    elif skill.observables[index2].level % 10 == 0 and skill.observables[index2].level != 0:
                        line.append('X')
                    else: line.append('')
                table.append(line)
                line_number += 1
            print(line_number)
        t = Table(table, colWidths=["*", None, None, None, None])
        t.setStyle(TableStyle(t_style))
        flowables.append(t)
    doc.build(flowables)


def build_diary(filename, date, day):
    doc = BaseDocTemplate(filename,
                          leftMargin=1 * cm,
                          rightMargin=1 * cm,
                          topMargin=1 * cm,
                          bottomMargin=1 * cm,
                          title=filename,
                          pagesize=A4,)

    doc.addPageTemplates(
        [
            PageTemplate(
                frames=[
                    Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        id='left',
                        #rightPadding=column_gap / 2,
                        showBoundary=0  # set to 1 for debugging
                    ),
                ],
                ),
        ]
    )

    flowables = list()
    flowables.append(Paragraph(date, stylesheet()['garde']), )
    flowables.append(Spacer(0, cm * 0.5))
    table = []
    if len(day['groups']) > 1:
        line1 = ['Horaire'] + ['%s' % g['name'] for g in day['groups']]  # 1 puis 2?
        table.append(line1)
    for index, item in enumerate(day['groups'][0]['items']):
        line = [item['schedule']]
        for g in day['groups']:
            f = []
            item = g['items'][index]
            f.append(Paragraph('<u>%s</u>' % item['description'], stylesheet()['default']))

            f.append(Paragraph('%s' % item['action_global'], stylesheet()['default']))
            line.append(f)

        table.append(line)

    cols = [1.5*cm]
    g_len = len(day['groups'])
    for c in range(g_len):
        cols.append((doc.width-1.5*cm)/g_len)
    print(g_len, cols, doc.width)
    t = Table(table, colWidths=cols)
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))
    flowables.append(t)
    doc.build(flowables)


def build_tasks(filename, day):
    w, h = A4
    doc = BaseDocTemplate(filename,
                          leftMargin=1 * cm,
                          rightMargin=1 * cm,
                          topMargin=1 * cm,
                          bottomMargin=1 * cm,
                          title=filename,
                          pagesize=(h, w,),)

    doc.addPageTemplates(
        [
            PageTemplate(
                frames=[
                    Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height,
                        id='left',
                        # rightPadding=column_gap / 2,
                        showBoundary=0  # set to 1 for debugging
                    ),
                    Frame(
                        doc.leftMargin + doc.width / 2,
                        doc.bottomMargin,
                        doc.width / 2,
                        doc.height,
                        id='right',
                        # leftPadding=column_gap / 2,
                        showBoundary=0
                    ),
                ]
            ),
        ]
    )
    flowables = list()

    t_style = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
               ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]

    for g in day['groups']:
        flowables.append(Paragraph(g['name'], stylesheet()['garde']), )
        flowables.append(Spacer(0, cm * .3))
        gap = 0
        table = []
        for index, item in enumerate(g["items"]):
            try:
                if item['description'] == g['items'][index+1]['description']:
                    gap += 1
                    continue
            except IndexError:
                pass
            line = []
            line.append(Paragraph(item['description'], stylesheet()['comp']), )
            if item["color"] == '':
                item["color"] = 'rgb(255, 255, 255)'
            t_style.append(('BACKGROUND', (0, index-gap), (0, index-gap), colors.toColor(item['color'])))
            if len(item['task']) > 0:
                line.append(Paragraph(item['task'], stylesheet()['comp']), )
                t_style.append(('BACKGROUND', (1, index-gap), (1, index-gap), colors.toColor(item['color'])))
            table.append(line)

        t = Table(table)
        t.setStyle(TableStyle(t_style))
        flowables.append(t)
        flowables.append(FrameBreak())
    doc.build(flowables)


def build_tt(filename, timetable):
    w, h = A4
    doc = BaseDocTemplate(filename,
                          leftMargin=1 * cm,
                          rightMargin=1 * cm,
                          topMargin=1 * cm,
                          bottomMargin=1 * cm,
                          title=filename,
                          pagesize=(h, w,),)
    doc.addPageTemplates(
        [
            PageTemplate(
                frames=[
                    Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        showBoundary=0  # set to 1 for debugging
                    ),
                ],
            ),
        ]
    )
    flowables = list()
    flowables.append(Paragraph('emploi du temps', stylesheet()['dom']))
    flowables.append(Spacer(0, cm * 0.5))

    table = []
    t_style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]

    days = [day['name'] for day in timetable]
    groups = [Paragraph(g['name'], stylesheet()['comp']) for g in timetable[0]['groups']]
    line1 = ['']
    for day in days:
        line1.append(Paragraph(day, stylesheet()['comp']))
        for _ in range(1, len(groups)):
            line1.append('')
    table.append(line1)

    line2 = ['']
    for _ in days:
        line2 += groups
    table.append(line2)

    ref = timetable[0]['groups'][0]['items']
    row_offset = 2
    for indexRow, item in enumerate(ref):
        line = [Paragraph(item['schedule'], stylesheet()['comp'])]
        for day in timetable:
            for grp in day['groups']:
                line.append(grp['items'][indexRow]['description'])
                # ajouter la couleur
                row = indexRow + row_offset
                t_style.append(('BACKGROUND', (len(line)-1, row), (len(line)-1, row), grp['items'][indexRow]['color']))
        table.append(line)


    # SPAN, (sc, sr), (ec, er)
    table2 = copy.deepcopy(table)
    #print(table)
    for indexrow, line in enumerate(table):
        print(line[1:])
        for indexcol, col in enumerate(line):
            if indexcol == 0: continue
            try:
                print(col == line[indexcol + 1], col, line[indexcol + 1])
                if col == line[indexcol + 1]:
                    col_offset = 1
                    #while line[indexcol + col_offset] == col:
                    table[indexrow][indexcol+col_offset] = ''
                    #col_offset += 1
                    t_style.append(('SPAN', (indexcol, indexrow), (indexcol + col_offset, indexrow)))
                if line[indexcol] == table[indexrow + 1][indexcol]:
                    pass
                    #table[indexrow + 1][indexcol] = ''
                    #if line[indexcol + 1] == col and col != '':
                    #table[indexrow][indexcol+1] = ''
                    #t_style.append(('SPAN', (indexcol, indexrow), (indexcol, indexrow+1)))
                    #continue
                    #else:
                    #t_style.append(('SPAN', (indexcol, indexrow), (indexcol, indexrow + 1)))
            except IndexError:
                pass

    # format table
    for indexrow, line in enumerate(table2):
        for indexcol, col in enumerate(line):
            if indexrow > 1 and indexcol > 0:
                table[indexrow][indexcol] = Paragraph(col, stylesheet()['default'])

    t = Table(table)

    # sapn days
    if len(groups) > 1:
        start = 1
        offset = len(groups) - 1
        for _ in days:
            t_style.append(('SPAN', (start, 0), (start+offset, 0)))
            start += len(groups)

    t.setStyle(TableStyle(t_style))
    flowables.append(t)
    doc.build(flowables)
