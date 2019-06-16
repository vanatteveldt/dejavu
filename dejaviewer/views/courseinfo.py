from typing import Iterable

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.views.generic import FormView, TemplateView

from dejaviewer.models import Course

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



class CourseInfoView(FormView):
    template_name = 'courseinfo.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.stepnr = kwargs.get('step', 1)
        self.step = steps[self.stepnr - 1]
        self.course = Course.objects.get(code="S_D1")

    def get_form_class(self):
        form = forms.Form
        for f in self.step.fields:
            form.base_fields[f.field] = forms.CharField(label=f.label,
                                                   widget=CKEditorWidget(),
                                                   initial=getattr(self.course, f.field))
        return form

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['course'] = self.course
        c['steps'] = steps
        c['step'] = self.step
        c['stepnr'] = self.stepnr
        c['nsteps'] = len(steps)
        return c


    def form_valid(self, form):
        for f in self.step.fields:
            print(f.field, form.cleaned_data[f.field])
            setattr(self.course, f.field, form.cleaned_data[f.field])
        self.course.save()
        return self.render_to_response(self.get_context_data(form=form))


class CourseInfoCompleteView(TemplateView):
    template_name = 'courseinfo_overview.html'

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
    template_name = 'courseinfo_index.html'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['course'] = Course.objects.get(id=kwargs['course'])
        c['steps'] = steps
        return c


