from django.urls import path

from dejaviewer.views import SyllabusView, IndexView
from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('syllabus', SyllabusView.as_view(), name='syllabus'),
]
