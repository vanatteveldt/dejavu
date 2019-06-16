from django.views.generic import TemplateView

from dejaviewer.models import Programme


class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        programmes = Programme.objects.all()

        context.update(**locals())
        return context