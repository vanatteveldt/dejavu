import argparse
import csv
import json
import re

import django
import os
from pathlib import Path
import logging

os.environ['DJANGO_SETTINGS_MODULE'] = 'dejavu.settings'

django.setup()
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')


from django.contrib.auth.models import User
from dejaviewer.models import Course, Year, Programme, Teacher, CourseTeacher


def path(fn):
    p = Path(fn)
    if not p.exists():
        raise IOError(f"File {p} does not exist")
    return p


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('uas_file', type=path)
args = parser.parse_args()

year = Year.objects.get(start_year=2019)


def get_teacher(c: Course, x: str) -> CourseTeacher:
    print(x)
    m = re.match(r"(prof. )?(drs. )?(?P<dr>dr. )?(?P<initials>[A-Z\.]+) (?P<name>[\w ]+?) (MSc )?\((?P<vunetid>\w+)\)", x)
    if not m:
        raise Exception(f"Could not parse teacher {x!r}")
    vunetid = m.group('vunetid')
    try:
        t = Teacher.objects.get(user__username=vunetid)
    except Teacher.DoesNotExist:
        try:
            u = User.objects.get(username=vunetid)
            logging.info(f"Creating teacher for {vunetid}")
        except User.DoesNotExist:
            logging.info(f"Creating new user {vunetid}")
            u = User.objects.create_user(username=vunetid,
                                         first_name=m.group('initials'),
                                         last_name=m.group('name'),
                                         email=f'{vunetid}@vu.nl')

            u.is_active = False
            u.save()
        t = Teacher.objects.create(user=u, has_phd=bool(m.group('dr')))
    ct, _created = CourseTeacher.objects.get_or_create(course=c, teacher=t)
    return ct


with args.uas_file.open() as f:
    for i, d in enumerate(csv.DictReader(f)):
        #print(json.dumps(d, indent=2))
        code = d['Code']
        print(i, code)
        continue
        try:
            c = Course.objects.get(code=code)
        except Course.DoesNotExist:
            c = Course()
            c.code = code
        c.year = year
        c.name = d['Vaknaam (EN)']

        if 'Bachelor jaar ' in d['Type']:
            c.curriculum_year = int(d['Type'].replace('Bachelor jaar ', ''))
        period = d['Aangeboden periodes'].replace("Periode ", "")
        if period == "4+5+6":
            period = 456
        if period == "5+6":
            period = 56
        if period == "1+2+3":
            period = 123
        if period == "Ac. Jaar (september)":
            period = 123456
        c.period = int(period)
        c.level = int(d['Niveau'])

        c.save()

        for code in d['Bijbehorende opleidingscodes'].split(", "):
            try:
                p = Programme.objects.get(code=code)
            except Programme.DoesNotExist:
                logging.warning(f"Skipping course {c} part of {code} ")
            c.programmes.add(p)

        #FIXME: handle EN
        c.description = d["Inhoud vak (studiegids) (NL)"]
        c.goal_text = d['Doel vak (studiegids) (NL)']
        #"Onderwijsvorm (studiegids) (NL)": "Hoor..."
        c.test_text = d["Toetsvorm (studiegids) (NL)"]
        c.literature = d["Literatuur (studiegids) (NL)"]

        for name in d['Vakcoordinator'].split(", "):
            if name:
                ct = get_teacher(c, name)
                ct.coordinator = True
                ct.save()
        for name in d['Examinator'].split(", "):
            if name:
                ct = get_teacher(c, name)
                ct.examinator = True
                ct.save()
        for name in d['Docent(en)'].split(", "):
            if name:
                get_teacher(c, name)
