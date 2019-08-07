import re
from typing import Iterable

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import CharField, modelformset_factory
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from dejaviewer.models import Course, CourseField, CourseInfo, LearningOutcome, TestType, Qualification


# Beschrijving (1.3) X
# Leerdoelen (2.2)   X
# Toetsing (2.1)     X

# Studiehandleiding (1.2)   > canvas?

# Toetsmatrijs (2.5 + 2.6)  > upload
# Tentamen + antwoordmodel + peer review (2.7 + 2.8)  > upload / canvas

# Evaluatievragen  > christoffel (gemaild voor N2)
# Tentamenanalyse + reactie  > upload + proza
# Reactie op evaluatie (3.3)  > proza

# Herentamenanalyse + reactie  > upload + proza


class DossierPartView(FormView):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.course = Course.objects.get(pk=kwargs['course'])
        self.course = Course.objects.get(pk=kwargs['course'])
        self.field = CourseField.objects.get(field=self.field)
        self.sources = {ci.source: ci.content for ci in CourseInfo.objects.filter(course=self.course, field=self.field)}
        self.value = self.sources.pop('dossier', '')

    @classmethod
    def is_complete(cls, course: Course) -> bool:
        return False

    def get_success_url(self):
        return reverse(self.view_name, kwargs=dict(course=self.course.id))


class DossierDescriptionForm(forms.Form):
    description = CharField(label='Coruse Description', widget=CKEditorWidget)


class DossierDescriptionView(DossierPartView):
    template_name = 'dossier_description.html'
    form_class = DossierDescriptionForm
    name = "Course Description"
    view_name = "dossier-description"
    field = 'description'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def get_initial(self):
        return {'description': self.value}

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['course'] = self.course
        c['sources'] = self.sources
        self.sources['Last year'] = '(sorry, no data yet!)'
        return c

    def form_valid(self, form):
        self.course.set_field('description', 'dossier', form.cleaned_data['description'])
        return super().form_valid(form)


    @classmethod
    def is_complete(cls, course: Course) -> bool:
        field = CourseField.objects.get(field='description')
        try:
            ci = CourseInfo.objects.get(field=field, course=course, source='dossier')
            return bool(ci.content.strip())
        except CourseInfo.DoesNotExist:
            return False


class DossierLearningGoalsView(DossierPartView):
    template_name = 'dossier_learninggoals.html'
    view_name = "dossier-goals"
    name = "Learning Goals"
    field = 'goal'
    form_class = modelformset_factory(LearningOutcome,
                                      exclude=['course'],
                                      can_delete=True,
                                      extra=1)

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['testtypes'] = list(TestType.objects.all())
        # monkey hack enters in UAS goals
        for src, text in self.sources.items():
            if 'UAS' in src:
                text = re.sub(r"([-A-Z])", r"<br/>\1", text)
                self.sources[src] = text
        c['sources'] = self.sources
        return c

    def get_form_class(self):
        # Filter qualifications of underlying form
        f = super().get_form_class()
        qualifications = Qualification.objects.filter(programme__in=self.course.programmes.all())

        class LearningOutcomeForm(f.form):
            def __init__(self, *args, **kargs):
                super().__init__(*args, **kargs)
                self.fields['qualification'].queryset = qualifications
        f.form = LearningOutcomeForm
        return f

    def form_valid(self, form):
        for goal in form.save(commit=False):
            goal.course = self.course
            goal.save()
        form.save_m2m()
        return super().form_valid(form)

    @classmethod
    def is_complete(cls, course: Course) -> bool:
        return Qualification.objects.filter(course=course).exists()

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
        course = Course.objects.get(id=kwargs['course'])
        parts = {p: p.is_complete(course) for p in dossier_parts}
        c.update(**locals())
        return c


dossier_parts = [DossierDescriptionView,
                 DossierLearningGoalsView,
                 ]
