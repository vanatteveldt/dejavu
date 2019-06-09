import argparse
import json
import os
import django
import logging


FSW_ACCOUNT = 18
CANVAS_URL = "https://canvas.vu.nl"

os.environ['DJANGO_SETTINGS_MODULE'] = 'dejavu.settings'

django.setup()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')

import canvasapi
from dejaviewer.models import Course, CourseField

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('apikey')
args = parser.parse_args()


canvas = canvasapi.Canvas(CANVAS_URL, args.apikey)

c = Course.objects.get(code="S_D1")
course = canvas.get_course(c.canvas_course, include=["syllabus_body"])
f = CourseField.objects.get(field='description')
c.set_field("description", "canvas syllabus", course.syllabus_body)
c.save()
