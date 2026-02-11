import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_voting.settings')
django.setup()

from core.models import User, Teacher, Student, Position, Candidate, ElectionSettings

def create_sample_data():
    print("Creating sample data...")

    # Create Principal
    if not User.objects.filter(username='principal').exists():
        principal = User.objects.create_superuser('principal', 'principal@school.com', 'admin123')
        principal.role = 'principal'
        principal.save()
        print("Created Principal: principal / admin123")

    # Create Teacher
    if not User.objects.filter(username='teacher1').exists():
        user = User.objects.create_user('teacher1', 'teacher1@school.com', 'teacher123', role='teacher')
        teacher = Teacher.objects.create(user=user, class_in_charge='10', section_in_charge='A')
        print("Created Teacher: teacher1 / teacher123")
    else:
        teacher = Teacher.objects.first()

    # Create Students
    students_data = [
        {'aadhaar': '111122223333', 'phone': '9876543210', 'name': 'John Doe'},
        {'aadhaar': '444455556666', 'phone': '9123456780', 'name': 'Jane Smith'},
        {'aadhaar': '777788889999', 'phone': '9988776655', 'name': 'Bob Wilson'},
    ]

    for data in students_data:
        if not User.objects.filter(username=data['aadhaar']).exists():
            user = User.objects.create_user(
                username=data['aadhaar'],
                password=data['phone'], # Phone is password
                first_name=data['name'].split()[0],
                last_name=data['name'].split()[1],
                role='student',
                phone=data['phone']
            )
            Student.objects.create(user=user, aadhaar=data['aadhaar'], class_name='10', section='A')
            print(f"Created Student: {data['name']} (Aadhaar: {data['aadhaar']} / Pass: {data['phone']})")

    # Create Position
    position, created = Position.objects.get_or_create(name='School Captain')
    if created:
        print("Created Position: School Captain")

    # Create Election Settings
    if not ElectionSettings.objects.exists():
        ElectionSettings.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=7)
        )
        print("Created Election Settings (Active for 7 days)")

    # Nominate Candidate
    student = Student.objects.first()
    if not Candidate.objects.filter(student=student, position=position).exists():
        Candidate.objects.create(
            student=student,
            position=position,
            manifesto="I promise to improve the sports facilities!",
            nominated_by=teacher
        )
        print(f"Nominated {student.user.get_full_name()} for {position.name}")

    print("Sample data creation complete.")

if __name__ == '__main__':
    create_sample_data()
