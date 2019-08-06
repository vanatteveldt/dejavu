from django.urls import path, reverse
from django.views.generic import RedirectView

from dejaviewer.views.auth import VULoginView, TokenLoginView
from dejaviewer.views.course import CourseView
from dejaviewer.views.dossier import CourseInfoCompleteView, CourseInfoIndexView, DossierDescriptionView, \
    DossierLearningGoalsView#, DossierEvaluationView, DossierTestView
from dejaviewer.views.curriculum import CurriculumView
from django.contrib.auth import views as auth_views

from dejaviewer.views.index import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('course/<int:course>/dossier/full', CourseInfoCompleteView.as_view(), name='course-info-complete'),
    path('course/<int:course>/dossier/description', DossierDescriptionView.as_view(), name=DossierDescriptionView.view_name),
    path('course/<int:course>/dossier/goals', DossierLearningGoalsView.as_view(), name=DossierLearningGoalsView.view_name),
    #path('course/<int:course>/dossier/test', DossierTestView.as_view(), name=DossierTestView.view_name),
    #path('course/<int:course>/dossier/evaluation', DossierEvaluationView.as_view(), name=DossierEvaluationView.view_name),
    path('course/<int:course>/dossier', CourseInfoIndexView.as_view(), name='course-info-index'),

    path('curriculum', CurriculumView.as_view(), name='curriculum'),
    path('curriculum/<str:programme>', CurriculumView.as_view(), name='curriculum'),

    path('course/<str:programme>/<int:course>', CourseView.as_view(), name='course'),
    path('course/<int:course>', CourseView.as_view(), name='course'),

    path('accounts/login/', VULoginView.as_view(), name='login'),
    path('accounts/login-token/<str:uidb64>/<str:token>/', TokenLoginView.as_view(), name='login-token'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
