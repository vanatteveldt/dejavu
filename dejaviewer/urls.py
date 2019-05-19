from django.urls import path

from dejaviewer.views import SyllabusView
from . import views

urlpatterns = [
    path('syllabus', SyllabusView.as_view(), name='syllabus'),
]
