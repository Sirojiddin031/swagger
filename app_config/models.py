
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator


# === USER MODEL ===
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The phone number must be set')
        extra_fields.setdefault('is_active', True)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,14}$',
        message="Phone number must be entered in the format: '998900404001'. Up to 14 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone


# === TOKEN MODEL ===
class TokenModel(models.Model):
    token = models.TextField()
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.created)


# === DEPARTMENTS & COURSE MODELS ===
class Departments(models.Model):
    title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title


# === WORKER, TEACHER & STUDENT MODELS ===
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker')
    departments = models.ManyToManyField(Departments, related_name='workers')
    course = models.ManyToManyField(Course, related_name='workers')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.phone


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    departments = models.ManyToManyField(Departments, related_name='teachers')
    description = models.TextField(blank=True, null=True)
    course = models.ManyToManyField(Course, related_name="teachers", through="TeacherCourse")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.user.full_name if self.user.full_name else self.user.phone


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, related_name='students')
    course = models.ManyToManyField(Course, related_name='students')
    is_line = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.full_name if self.user.full_name else self.user.phone


class Parents(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="parent")
    full_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name if self.full_name else "Unknown Parent"


# === GROUP MODEL ===
class Group(models.Model):
    title = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT, related_name='groups')
    teacher = models.ManyToManyField(Teacher, related_name="groups")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.CharField(max_length=15, blank=True, null=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


# === ATTENDANCE MODELS ===
class AttendanceLevel(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


class Attendance(models.Model):
    level = models.ForeignKey(AttendanceLevel, on_delete=models.RESTRICT, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.RESTRICT, related_name='attendances')
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, related_name='attendances')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.level}"


# === HOMEWORK MODELS ===
class Topics(models.Model):
    title = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT, related_name='topics')
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


class GroupHomeWork(models.Model):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, related_name='group_homeworks')
    topic = models.ForeignKey(Topics, on_delete=models.RESTRICT, related_name='group_homeworks')
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)


class HomeWork(models.Model):
    groupHomeWork = models.ForeignKey(GroupHomeWork, on_delete=models.RESTRICT, related_name='homeworks')
    student = models.ForeignKey(Student, on_delete=models.RESTRICT, related_name='homeworks')
    link = models.URLField()
    is_active = models.BooleanField(default=False)
    descriptions = models.CharField(max_length=500, blank=True, null=True)


# === DAY, ROOMS, TABLE MODELS ===
class Day(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


class Rooms(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


class TableType(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


class Table(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Rooms, on_delete=models.RESTRICT, related_name='tables')
    type = models.ForeignKey(TableType, on_delete=models.RESTRICT, related_name='tables')
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


# === PAYMENT MODELS ===
class PaymentType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.amount}"


# === TEACHER RELATIONS ===
class TeacherCourse(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class TeacherDepartments(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)


class Subject(models.Model):
    title = models.CharField(max_length=50, verbose_name="Nomi")  
    descriptions = models.CharField(max_length=500, null=True, blank=True, verbose_name="Tavsif")  
    is_active = models.BooleanField(default=True, verbose_name="Faolmi") 

    def __str__(self):
        return self.title  

    class Meta:
        verbose_name = "Fan"  
        verbose_name_plural = "Fanlar" 

# === COMMENT MODEL ===
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
