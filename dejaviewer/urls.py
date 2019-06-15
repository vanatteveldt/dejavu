from django.urls import path, reverse
from django.views.generic import RedirectView

from dejaviewer.views import CourseInfoView, IndexView
from dejaviewer.views.course import CourseView
from dejaviewer.views.courseinfo import CourseInfoOverView
from dejaviewer.views.curriculum import CurriculumView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('course-info/overview', CourseInfoOverView.as_view(), name='course-info'),
    path('course-info/<int:step>', CourseInfoView.as_view(), name='course-info'),
    path('course-info', RedirectView.as_view(url='/course-info/1'), name='course-info-index'),
    path('curriculum', CurriculumView.as_view(), name='curriculum'),
    path('curriculum/<str:programme>', CurriculumView.as_view(), name='curriculum'),
    path('curriculum/<str:programme>/<str:course>', CourseView.as_view(), name='course'),
]
