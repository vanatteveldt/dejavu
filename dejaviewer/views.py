from ckeditor.widgets import CKEditorWidget
from django.shortcuts import render

from django import forms
from django.views.generic import FormView
from tinymce.widgets import TinyMCE


class ContactForm(forms.Form):
    content = forms.CharField(widget=CKEditorWidget())

class SyllabusView(FormView):
    template_name = 'syllabus.html'
    form_class = ContactForm
    success_url = '/thanks/'

