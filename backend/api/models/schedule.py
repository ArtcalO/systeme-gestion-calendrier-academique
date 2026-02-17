from django.db import models
from .academic import Department
class TimeSlot(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]
    
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_type = models.CharField(max_length=20, choices=[
        ('lecture', 'Lecture'),
        ('tutorial', 'Tutorial'),
        ('practical', 'Practical'),
        ('lab', 'Lab')
    ])

class Room(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=[
        ('lecture', 'Lecture Hall'),
        ('tutorial', 'Tutorial Room'),
        ('lab', 'Laboratory'),
        ('computer', 'Computer Lab')
    ])
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    facilities = models.JSONField(default=list)  # ['projector', 'ac', 'whiteboard']

class ScheduleConstraint(models.Model):
    name = models.CharField(max_length=100)
    constraint_type = models.CharField(max_length=30, choices=[
        ('room_capacity', 'Room Capacity'),
        ('teacher_availability', 'Teacher Availability'),
        ('department_preference', 'Department Preference'),
        ('time_preference', 'Time Preference'),
        ('consecutive_classes', 'Consecutive Classes')
    ])
    parameters = models.JSONField()  # Flexible parameters storage
    weight = models.IntegerField(default=1)  # Constraint importance
    is_hard = models.BooleanField(default=True)