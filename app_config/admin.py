from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


class UserAdmin(BaseUserAdmin):
    list_display = ('phone', 'full_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone', 'full_name')
    ordering = ('phone',)
# **Barcha modellarni oddiy usulda ro'yxatga olish**
admin.site.register(User)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Payment)
admin.site.register(Subject)
admin.site.register(TokenModel)
admin.site.register(Course)
admin.site.register(Departments)
admin.site.register(Worker)
admin.site.register(Group)
admin.site.register(Parents)
admin.site.register(Attendance)
admin.site.register(AttendanceLevel)
admin.site.register(Topics)
admin.site.register(GroupHomeWork)
admin.site.register(HomeWork)
admin.site.register(Day)
admin.site.register(Rooms)
admin.site.register(TableType)
admin.site.register(Table)
admin.site.register(PaymentType)
admin.site.register(TeacherCourse)
admin.site.register(TeacherDepartments)
admin.site.register(Comment)