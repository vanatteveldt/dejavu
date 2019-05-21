from ckeditor.widgets import CKEditorWidget
from django.shortcuts import render

from django import forms
from django.views.generic import FormView, TemplateView
from tinymce.widgets import TinyMCE

from dejaviewer.models import Course


class ContactForm(forms.Form):
    content = forms.CharField(widget=CKEditorWidget())

class SyllabusView(FormView):
    template_name = 'syllabus.html'
    form_class = ContactForm
    success_url = '/thanks/'



class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        return context