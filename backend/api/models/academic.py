from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class AcademicYear(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

class Module(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    credits = models.IntegerField()
    semester = models.IntegerField(choices=[(1, 'S1'), (2, 'S2')])
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    hours_per_week = models.IntegerField()
    lecture_hours = models.IntegerField()
    tutorial_hours = models.IntegerField()
    practical_hours = models.IntegerField()

class Prerequisite(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='dependencies')
    prerequisite_module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='required_for')
    is_mandatory = models.BooleanField(default=True)
    min_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    current_semester = models.IntegerField()
    enrollment_year = models.IntegerField()
    is_active = models.BooleanField(default=True)

class StudentModuleRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.IntegerField()
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ])