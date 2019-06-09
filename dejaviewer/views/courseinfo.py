from typing import Iterable

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.views.generic import FormView

from dejaviewer.models import Course

class Field:
    def __init__(self, field: str, label: str):
        self.field = field
        self.label = label

class Step:
    def __init__(self, name: str, fields: Iterable[Field]):
        self.name = name
        self.fields = fields


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

steps = [
    Step("Course Description", [Field("description", "Course Description"),
                                Field("goal_text", "Course goals")]),
    Step("Syllabus and course manual", [Field("syllabus", "Syllabus")]),
]


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
