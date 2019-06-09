from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from dejaviewer.models import CourseTeacher, CourseInfo
from .models import Year, Course, Qualification, Programme, TestType, Teacher

# Register your models here.

admin.site.register(Year)
admin.site.register(Qualification)
admin.site.register(Programme)
admin.site.register(TestType)

class CourseInfoInline(admin.TabularInline):
    model = CourseInfo
    extra = 2

class CourseTeacherInline(admin.TabularInline):
    model = CourseTeacher
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = (CourseInfoInline, CourseTeacherInline,)
admin.site.register(Course, CourseAdmin)

admin.site.unregister(User)


class TeacherInline(admin.StackedInline):
    model = Teacher


class CustomUserAdmin(UserAdmin):
    #filter_horizontal = ('user_permissions', 'groups', 'ope')
    save_on_top = True
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login')
    inlines = [TeacherInline]


admin.site.register(User, CustomUserAdmin)