from typing import Iterable

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import CharField
from django.views.generic import FormView, TemplateView

from dejaviewer.models import Course, CourseField, CourseInfo

# Beschrijving (1.3)
# Leerdoelen (2.2)
# Toetsing (2.1)

# Studiehandleiding (1.2)

# Toetsmatrijs (2.5 + 2.6)
# Tentamen + antwoordmodel + peer review (2.7 + 2.8)

# Evaluatievragen
# Tentamenanalyse + reactie
# Reactie op evaluatie (3.3)

# Herentamenanalyse + reactie

steps = {
    "Description": ["description", "goal"],
    "Course Manual": [],
    "Testing": ["test"],
    "Evaluation": [],
    "Resit": [],
}



class DossierDescriptionForm(forms.Form):
    description = CharField(label='Coruse Description', widget=CKEditorWidget)

class DossierDescriptionView(FormView):
    template_name = 'dossier_description.html'
    form_class = DossierDescriptionForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.course = Course.objects.get(pk=kwargs['course'])
        self.field = CourseField.objects.get(field='description')
        self.sources = {ci.source: ci.content for ci in CourseInfo.objects.filter(course=self.course, field=self.field)}
        self.value = self.sources.pop('dossier', '')
        self.sources['Last year'] = '(sorry, no data yet!)'

    def get_initial(self):
        return {'description': self.value}

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['course'] = self.course
        c['sources'] = self.sources
        return c

    def form_valid(self, form):
        self.course.set_field('description', 'dossier', form.cleaned_data['description'])
        return super().form_valid(form)


class CourseInfoCompleteView(TemplateView):
    template_name = 'dossier_full.html'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        course = Course.objects.get(code="S_D1")
        fields = {}
        for ci in course.courseinfo_set.all():
            if ci.field not in fields:
                fields[ci.field] = {}
            fields[ci.field][ci.source] = ci.content
        c.update(dict(course=course, fields=fields))
        return c


class CourseInfoIndexView(TemplateView):
    template_name = 'dossier_index.html'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['course'] = Course.objects.get(id=kwargs['course'])
        c['steps'] = steps
        return c

