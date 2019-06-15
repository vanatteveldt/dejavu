from django.views.generic import TemplateView

from dejaviewer.models import Programme


class CurriculumView(TemplateView):
    template_name = 'curriculum.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if 'programme' in kwargs:
            programme = Programme.objects.get(code=kwargs['programme'])
        else:
            programme = Programme.objects.all()[0]
        programmes = Programme.objects.all()
        courses = programme.course_set.all().order_by('period')
        ctx.update(**locals())
        return ctx

