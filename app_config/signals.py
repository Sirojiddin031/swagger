from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Teacher, Student

@receiver(post_save, sender=Teacher)
def add_teacher_to_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="Teachers")
        instance.user.groups.add(group)
        instance.user.is_teacher = True
        instance.user.is_staff = True  # 🔥 O‘qituvchi admin panelga kira oladi
        instance.user.save()

@receiver(post_save, sender=Student)
def add_student_to_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="Students")
        instance.user.groups.add(group)
        instance.user.is_student = True
        instance.user.is_staff = False  # 🔥 Student admin panelga kira olmaydi
        instance.user.save()
