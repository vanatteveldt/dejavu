from django.views.generic import TemplateView

from dejaviewer.models import Programme, Course, CourseTeacher


class CourseView(TemplateView):
    template_name = 'course.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        programmes = Programme.objects.all()
        programme = Programme.objects.get(code=kwargs['programme']) if 'programme' in kwargs else None

        courses = programme.course_set.all()
        course = Course.objects.get(pk=kwargs['course'])
        teachers = CourseTeacher.objects.filter(course=course)

        if False and user.is_superuser:
            can_edit = True
        elif user.is_authenticated:
            try:
                ct = CourseTeacher.objects.get(course=course, teacher__user=user)
                can_edit = ct.coordinator
            except CourseTeacher.DoesNotExist:
                can_edit = False

        ctx.update(**locals())
        return ctx


