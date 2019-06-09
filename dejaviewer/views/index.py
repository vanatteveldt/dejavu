from django.views.generic import TemplateView

from dejaviewer.models import Programme


class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # set up dict of courses per period, and register ribbon courses
        # (so 123 -> course in p3 and ribbon in 1 and 2)
        periods = {p: [] for p in range(1, 7)}
        ribbons = {}
        courses  = (Programme.objects.get(code="SB_CW").course_set
                       .filter(programme_year=1, academic_year__start_year=2019, language="EN")
                    )
        for c in courses:
            p = c.period
            rr = []
            if c.period == 123:
                p = 3
                rr = [1,2]
            elif c.period == 456:
                p = 6
                rr = [4,5]
            periods[p].append(c)
            ribbons.update({r: c for r in rr})

        context['periods'] = periods
        context['ribbons'] = ribbons
        print(periods)
        return context