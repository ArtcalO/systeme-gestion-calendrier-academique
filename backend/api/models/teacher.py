from django.db import models
from .academic import Department, Module, AcademicYear
from .schedule import Room, TimeSlot
class Teacher(models.Model):
    teacher_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    max_weekly_hours = models.IntegerField(default=20)
    min_weekly_hours = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive')
    ])

class TeacherAvailability(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), ...])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True)

class TeacherSpecialization(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=[
        ('expert', 'Expert'),
        ('proficient', 'Proficient'),
        ('capable', 'Capable'),
        ('basic', 'Basic')
    ])
    years_experience = models.IntegerField(default=0)

class ClassAssignment(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.IntegerField()
    assigned_hours = models.IntegerField()
    assignment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', ''),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ])