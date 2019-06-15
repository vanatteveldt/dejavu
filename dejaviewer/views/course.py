from django.views.generic import TemplateView

from dejaviewer.models import Programme, Course, CourseTeacher


class CourseView(TemplateView):
    template_name = 'course.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        programmes = Programme.objects.all()
        programme = Programme.objects.get(code=kwargs['programme'])
        courses = programme.course_set.all()
        course = Course.objects.get(code=kwargs['course'])
        teachers = CourseTeacher.objects.filter(course=course)
        ctx.update(**locals())
        return ctx


