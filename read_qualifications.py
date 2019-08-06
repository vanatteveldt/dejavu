import os, django, logging

os.environ['DJANGO_SETTINGS_MODULE'] = 'dejavu.settings'

django.setup()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')

import csv, sys
from dejaviewer.models import Qualification, Programme

for line in csv.DictReader(sys.stdin):
    nr = line['nr']
    p = Programme.objects.get(code=line['programme'])
    try:
        q = Qualification.objects.get(programme=p, nr=nr)
    except Qualification.DoesNotExist:
        q = Qualification(programme=p, nr=nr)

    q.category = line['category']
    q.nr = line['nr']
    q.label = line['label']
    q.description = line['description']
    q.save()