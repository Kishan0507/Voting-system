import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_voting.settings')
django.setup()

from core.models import User, Teacher, Student, Position
from faker import Faker
from django.db import IntegrityError

def run_seed():
    fake = Faker('en_IN')
    
    print("🧹 Clearing old non-superuser data...")
    # Delete students, teachers, positions, candidates, votes
    Student.objects.all().delete()
    Teacher.objects.all().delete()
    Position.objects.all().delete()
    
    # Delete users that are not superusers
    User.objects.filter(is_superuser=False).delete()

    print("👑 Creating/Fetching Principal...")
    try:
        principal_user, created = User.objects.get_or_create(
            username='principal',
            defaults={
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': 'principal@school.com',
                'role': 'principal',
                'phone': str(fake.random_number(digits=10, fix_len=True))
            }
        )
        principal_user.set_password('password123')
        principal_user.role = 'principal'
        principal_user.save()
    except IntegrityError:
        print("Principal user already exists as a superuser. Skipping creation.")

    print("👩‍🏫 Creating 10 Teachers...")
    classes = ['9th', '10th', '11th', '12th']
    sections = ['A', 'B', 'C', 'D']
    
    teachers = []
    combinations = [(c, s) for c in classes for s in sections]
    random.shuffle(combinations)

    for i in range(10):
        c, s = combinations[i % len(combinations)]
        phone = str(fake.random_number(digits=10, fix_len=True))
        
        # Ensure unique username
        username = f'teacher{i+1}'
        User.objects.filter(username=username).delete()
        
        t_user = User.objects.create_user(
            username=username,
            password='password123',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            role='teacher',
            phone=phone
        )
        teacher = Teacher.objects.create(
            user=t_user,
            class_in_charge=c,
            section_in_charge=s
        )
        teachers.append(teacher)
        
    print("🎓 Creating 100 students for each teacher (1000 total students)...")
    for teacher in teachers:
        print(f"   -> Assigning 100 students to Teacher {teacher.user.first_name} (Class {teacher.class_in_charge}-{teacher.section_in_charge})")
        for _ in range(100):
            # Generate unique aadhaar manually or rely on Faker's uniqueness
            aadhaar = str(fake.unique.random_number(digits=12, fix_len=True))
            phone = str(fake.random_number(digits=10, fix_len=True))
            
            s_user = User.objects.create_user(
                username=aadhaar,
                password=phone,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='student',
                phone=phone
            )
            
            Student.objects.create(
                user=s_user,
                aadhaar=aadhaar,
                class_name=teacher.class_in_charge,
                section=teacher.section_in_charge
            )
            
    print("🏆 Creating common election positions...")
    positions = ['School President', 'Vice President', 'Sports Captain', 'Cultural Secretary', 'Discipline Head']
    for pos_name in positions:
        Position.objects.get_or_create(name=pos_name)
    
    print("\n✅ Seeding Complete!\n")
    print("--- LOGIN CREDENTIALS ---")
    print("Principal Username : principal")
    print("Principal Password : password123")
    print("-------------------------")
    print("Teacher Usernames  : teacher1 through teacher10")
    print("Teacher Passwords  : password123")
    print("-------------------------")
    print("Student Logins are based on their Aadhaar Number and Phone Number.")

if __name__ == '__main__':
    run_seed()
