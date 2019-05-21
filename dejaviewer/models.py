from django.contrib.auth.models import User
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_phd = models.BooleanField(null=True)
    has_bko = models.BooleanField(null=True)
    has_enc1 = models.BooleanField(null=True)
    notes = models.TextField()

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

    def __str__(self):
        return f'{self.name}'


class Course(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year, on_delete=models.PROTECT)
    period = models.IntegerField()  # p1 .. p6
    teachers = models.ManyToManyField(Teacher, through='CourseTeacher')
    outcomes = models.ManyToManyField(Qualification, through='LearningOutcome')
    programmes = models.ManyToManyField(Programme)

    level = models.IntegerField()
    curriculum_year = models.IntegerField(null=True)

    description = models.TextField()  # Inhoud vak (studiegids)
    goal_text = models.TextField()    # Doel vak (studiegids)
    test_text = models.TextField()    # Toetsvorm (studiegids)
    literature = models.TextField()

    def __str__(self):
        return f'[{self.code}] {self.name}'


class CourseTeacher(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    coordinator = models.BooleanField(default=False)
    examinator = models.BooleanField(default=False)


class TestType(models.Model):
    name = models.CharField(max_length=100)


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    type = models.ForeignKey(TestType, on_delete=models.PROTECT)


class LearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT)
    tested = models.ManyToManyField(Test)
