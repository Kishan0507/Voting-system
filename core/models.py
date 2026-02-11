from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CHOICES = (
        ('principal', 'Principal'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def is_principal(self):
        return self.role == 'principal'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    class_in_charge = models.CharField(max_length=10, blank=True, null=True)
    section_in_charge = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    aadhaar = models.CharField(max_length=12, unique=True)
    class_name = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.class_name}-{self.section})"

class Candidate(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    manifesto = models.TextField()
    photo = models.ImageField(upload_to='candidates/')
    nominated_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} for {self.position.name}"
    
    class Meta:
        unique_together = ('student', 'position')

class ElectionSettings(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def save(self, *args, **kwargs):
        if not self.pk and ElectionSettings.objects.exists():
            raise ValidationError('There can be only one ElectionSettings instance')
        return super(ElectionSettings, self).save(*args, **kwargs)

    def __str__(self):
        return f"Election: {self.start_time} to {self.end_time}"

class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'position')

    def save(self, *args, **kwargs):
        settings = ElectionSettings.objects.first()
        if not settings or not settings.is_active():
            raise ValidationError("Election is not currently active.")
        super().save(*args, **kwargs)

class Broadcast(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    attachment = models.FileField(upload_to='broadcasts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
