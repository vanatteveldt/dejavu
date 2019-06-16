from django.urls import path, reverse
from django.views.generic import RedirectView

from dejaviewer.views import CourseInfoView, IndexView
from dejaviewer.views.course import CourseView
from dejaviewer.views.courseinfo import CourseInfoCompleteView, CourseInfoIndexView
from dejaviewer.views.curriculum import CurriculumView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('course/<int:course>/dossier/full', CourseInfoCompleteView.as_view(), name='course-info-complete'),
    path('course/<int:course>/dossier/<int:step>', CourseInfoView.as_view(), name='course-info'),
    path('course/<int:course>/dossier', CourseInfoIndexView.as_view(), name='course-info-index'),

    path('curriculum', CurriculumView.as_view(), name='curriculum'),
    path('curriculum/<str:programme>', CurriculumView.as_view(), name='curriculum'),

    path('course/<str:programme>/<int:course>', CourseView.as_view(), name='course'),
    path('course/<int:course>', CourseView.as_view(), name='course'),
]
