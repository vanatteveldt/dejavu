from django.contrib import admin
from .models import Year, Course, Qualification, Programme, TestType

# Register your models here.

admin.site.register(Year)
admin.site.register(Course)
admin.site.register(Qualification)
admin.site.register(Programme)
admin.site.register(TestType)
