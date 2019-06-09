import argparse
import csv
import json
import re
from collections import namedtuple
from typing import Match, List

import django
import os
from pathlib import Path
import logging

# "Onderwijsvorm (studiegids) (NL)": "Hoor..."
#c.literature = d["Literatuur (studiegids) (NL)"]

Field = namedtuple('Field', ["field", "source", "column"])

fields = [
    Field("description", "UAS (NL)", "Inhoud vak (studiegids) (NL)"),
    Field("description", "UAS (EN)", "Inhoud vak (studiegids) (EN)"),

    Field("goal", "UAS (NL)", "Doel vak (studiegids) (NL)"),
    Field("goal", "UAS (EN)", "Doel vak (studiegids) (EN)"),

    Field("test", "UAS (NL)", "Toetsvorm (studiegids) (NL)"),
    Field("test", "UAS (EN)", "Toetsvorm (studiegids) (EN)"),
]  # type: List[Field]


# 1. go to https://uas.vu.nl/#/study/986/modules
# 2. change 'vakken van de opleiding' to  'binnen faculteit'
# 3. select kolommen -. toon alles
# 4. wait a minute to allow columns to load (yes, really)
# 5. click download -> csv
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'dejavu.settings'

django.setup()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')

codes = {x['code'] for x in csv.DictReader(open("data/cw_vakken.csv"))}

from django.contrib.auth.models import User
from dejaviewer.models import Course, Year, Programme, Teacher, CourseTeacher, CourseField, CourseInfo


def path(fn):
    p = Path(fn)
    if not p.exists():
        raise IOError(f"File {p} does not exist")
    return p


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('uas_file', type=path)
args = parser.parse_args()

year = Year.objects.get(start_year=2019)


def rematch(pattern: str, string:str, *args, **kargs) -> Match:
    m = re.match(pattern, string, *args, **kargs)
    if not m:
        raise Exception(f"Cannot parse {string!r}")
    return m


def research(pattern: str, string:str, *args, **kargs) -> Match:
    m = re.search(pattern, string, *args, **kargs)
    if not m:
        raise Exception(f"Cannot parse {string!r}")
    return m


def get_teacher(c: Course, x: str) -> CourseTeacher:
    m = rematch(r"(?P<titles>(prof. |mr. |drs. |ir. |dr. )*)(?P<initials>[A-Z\.]+) (?P<name>[-\w ]+?) (MA.? |MSc.? )*\((?P<vunetid>\w+)\)", x)
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
        phd = 'dr.' in m.group('titles')
        t = Teacher.objects.create(user=u, has_phd=phd)
    ct, _created = CourseTeacher.objects.get_or_create(course=c, teacher=t)
    return ct


with args.uas_file.open() as f:
    for i, d in enumerate(csv.DictReader(f)):
        #print(json.dumps(d, indent=2))
        code = d['Code']
        if code not in codes:
            continue
        codes.remove(code)
        print(i, code, d['Vaknaam (EN)'])
        try:
            c = Course.objects.get(code=code)
        except Course.DoesNotExist:
            c = Course()
            c.code = code

        # skip courses with no period
        period = d['Aangeboden periodes'].replace("Periode ", "")
        if not period.strip():
            continue
        if period == "Ac. Jaar (september)":
            c.period = 123456
        else:
            c.period = int(re.sub(r"\+", "", period))

        c.academic_year = year
        c.name = d['Vaknaam (EN)']
        if d['Onderwijstaal']:
            m = research(r"\((\w+)\)", d['Onderwijstaal'])
            c.language = m.group(1)
        if 'Bachelor jaar ' in d['Type']:
            c.programme_year = int(d['Type'].replace('Bachelor jaar ', ''))

        if d['Niveau']:
            c.level = int(d['Niveau'])

        # FIXME: get proper course ids (from somewhere)
        if c.code == "S_D1":
            c.canvas_course = 38555

        c.save()  # id needed to make many-to-many relations

        for field in fields:
            content = d[field.column]
            if content:
                c.set_field(field.field, field.source, content)

        for code in set(d['Bijbehorende opleidingscodes'].split(", ")):
            try:
                p = Programme.objects.get(code=code)
                c.programmes.add(p)
            except Programme.DoesNotExist:
                pass

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
            if name and not name == "houtveen":
                get_teacher(c, name)
