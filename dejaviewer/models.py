from django.contrib.auth.models import User
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_phd = models.BooleanField(null=True)
    has_bko = models.BooleanField(null=True)
    has_enc1 = models.BooleanField(null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'[{self.user.username}] {self.user.first_name} {self.user.last_name}'


class Year(models.Model):
    start_year = models.IntegerField()

    def __str__(self):
        return f'{self.start_year}-{self.start_year+1}'


class Programme(models.Model):  # BA, P, M, ...
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Qualification(models.Model):  # eindterm
    name = models.CharField(max_length=100)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    category = models.TextField()
    nr = models.CharField(max_length=5)
    label = models.TextField()
    description = models.TextField()

    def __str__(self):
        return f'[{self.nr}] {self.category}: {self.label}'

    class Meta:
        ordering = ['nr']
        unique_together = ['programme', 'nr']


class Course(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey(Year, on_delete=models.PROTECT)
    period = models.IntegerField()  # p1 .. p6
    teachers = models.ManyToManyField(Teacher, through='CourseTeacher')
    outcomes = models.ManyToManyField(Qualification, through='LearningOutcome')
    programmes = models.ManyToManyField(Programme)
    ba_year = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=2)
    canvas_course = models.IntegerField(null=True, blank=True)

    level = models.IntegerField(null=True)

    def __str__(self):
        return f'[{self.code}] {self.name}'

    def set_field(self, field: str, source: str, content: str):
        f, _created = CourseField.objects.get_or_create(field=field)
        try:
            ci = CourseInfo.objects.get(course=self, field=f, source=source)
            ci.content = content
            ci.save()
        except CourseInfo.DoesNotExist:
            CourseInfo.objects.create(course=self, field=f, source=source, content=content)


class CourseField(models.Model):
    field = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.field}'


class CourseInfo(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    field = models.ForeignKey(CourseField, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    content = models.TextField(null=False, blank=False)

    class Meta:
        unique_together = ["course", "field", "source"]

    def __str__(self):
        return f'{self.course.code}.{self.field} ({self.source})'


class CourseTeacher(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    coordinator = models.BooleanField(default=False)
    examinator = models.BooleanField(default=False)


class TestType(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.name}'


class LearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT)
    description = models.TextField(null=False, blank=False)
    tested = models.ManyToManyField(TestType)

    class Meta:
        ordering = ['qualification']