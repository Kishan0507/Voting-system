from django.contrib import admin
from .models import User, Teacher, Student, Position, Candidate, ElectionSettings, Vote, Broadcast

admin.site.register(User)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Position)
admin.site.register(Candidate)
admin.site.register(ElectionSettings)
admin.site.register(Vote)
admin.site.register(Broadcast)
