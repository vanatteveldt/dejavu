from django.urls import path, reverse
from django.views.generic import RedirectView

from dejaviewer.views import CourseInfoView, IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('course-info/<int:step>', CourseInfoView.as_view(), name='course-info'),
    path('course-info', RedirectView.as_view(url='/course-info/1'), name='course-info-index'),
]
