import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponse
from .forms_new import (
    PrincipalLoginForm, TeacherLoginForm, StudentLoginForm,
    TeacherCreationForm, StudentCreationForm, PositionForm,
    CandidateNominationForm, BroadcastForm, ElectionSettingsForm,
    PrincipalCreationForm
)
from .models import User, Teacher, Student, Position, Candidate, Vote, Broadcast, ElectionSettings

def index(request):
    if request.user.is_authenticated:
        if request.user.is_principal():
            return redirect('principal_dashboard')
        elif request.user.is_teacher():
            return redirect('teacher_dashboard')
        elif request.user.is_student():
            return redirect('student_dashboard')
            
    if request.method == 'POST':
        form = PrincipalLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('principal_dashboard')
    else:
        form = PrincipalLoginForm()
    return render(request, 'login.html', {'form': form, 'role': 'Principal'})

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('teacher_dashboard')
    else:
        form = TeacherLoginForm()
    return render(request, 'login.html', {'form': form, 'role': 'Teacher'})

def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            aadhaar = form.cleaned_data['aadhaar']
            phone = form.cleaned_data['phone']
            user = authenticate(username=aadhaar, password=phone)
            if user:
                login(request, user)
                return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = StudentLoginForm()
    return render(request, 'login.html', {'form': form, 'role': 'Student'})

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def principal_dashboard(request):
    if not request.user.is_principal(): return redirect('index')
    
    teachers = Teacher.objects.all()
    students = Student.objects.all()
    candidates = Candidate.objects.all()
    students_count = students.count()
    candidates_count = candidates.count()
    votes_count = Vote.objects.count()
    broadcasts = Broadcast.objects.all().order_by('-created_at')
    
    election_settings = ElectionSettings.objects.first()
    
    context = {
        'teachers': teachers,
        'students': students,
        'candidates': candidates,
        'students_count': students_count,
        'candidates_count': candidates_count,
        'votes_count': votes_count,
        'broadcasts': broadcasts,
        'election_settings': election_settings,
    }
    return render(request, 'principal_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher(): return redirect('index')
    
    teacher = request.user.teacher_profile
    students = Student.objects.filter(class_name=teacher.class_in_charge, section=teacher.section_in_charge)
    nominated_candidates = Candidate.objects.filter(nominated_by=teacher)
    settings = ElectionSettings.objects.first()
    
    context = {
        'teacher': teacher,
        'students': students,
        'nominated_candidates': nominated_candidates,
        'settings': settings,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def student_dashboard(request):
    if not request.user.is_student(): return redirect('index')
    
    student = request.user.student_profile
    positions = Position.objects.all()
    # Check which positions the student has voted for
    voted_positions = list(Vote.objects.filter(student=student).values_list('position_id', flat=True))
    settings = ElectionSettings.objects.first()
    
    context = {
        'student': student,
        'positions': positions,
        'voted_positions': voted_positions,
        'settings': settings,
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def add_teacher(request):
    if not request.user.is_principal(): return redirect('index')
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher added successfully')
            return redirect('principal_dashboard')
    else:
        form = TeacherCreationForm()
    return render(request, 'form.html', {'form': form, 'title': 'Add Teacher'})

@login_required
def add_student(request):
    if not request.user.is_teacher() and not request.user.is_principal(): return redirect('index')
    
    teacher = request.user.teacher_profile if request.user.is_teacher() else None
    
    if request.method == 'POST':
        form = StudentCreationForm(request.POST, teacher=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully')
            return redirect('teacher_dashboard') if request.user.is_teacher() else redirect('principal_dashboard')
    else:
        form = StudentCreationForm(teacher=teacher)
    return render(request, 'form.html', {'form': form, 'title': 'Add Student'})

@login_required
def nominate_candidate(request):
    if not request.user.is_teacher(): return redirect('index')
    teacher = request.user.teacher_profile
    if request.method == 'POST':
        form = CandidateNominationForm(request.POST, request.FILES)
        form.fields['student'].queryset = Student.objects.filter(class_name=teacher.class_in_charge, section=teacher.section_in_charge)
        if form.is_valid():
            # Check for existing nomination in ANY position
            student = form.cleaned_data['student']
            position = form.cleaned_data['position']
            
            if Candidate.objects.filter(student=student).exists():
                messages.error(request, f'This student is already nominated as a candidate for another position.')
            else:
                candidate = form.save(commit=False)
                candidate.student = student
                candidate.nominated_by = teacher
                candidate.save()
                messages.success(request, 'Candidate nominated successfully')
                return redirect('teacher_dashboard')
    else:
        form = CandidateNominationForm()
        form.fields['student'].queryset = Student.objects.filter(class_name=teacher.class_in_charge, section=teacher.section_in_charge)
    return render(request, 'form.html', {'form': form, 'title': 'Nominate Candidate'})

@login_required
def vote_page(request, position_id):
    if not request.user.is_student(): return redirect('index')
    position = get_object_or_404(Position, id=position_id)
    student = request.user.student_profile
    
    # Check if election is active
    settings = ElectionSettings.objects.first()
    if not settings or not settings.is_active():
        messages.error(request, 'Election is not currently active.')
        return redirect('student_dashboard')

    if Vote.objects.filter(student=student, position=position).exists():
        messages.warning(request, 'You have already voted for this position.')
        return redirect('student_dashboard')
        
    candidates = Candidate.objects.filter(position=position)
    
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        
        # Security Patch: Ensure candidate belongs to the current position
        if candidate.position != position:
            messages.error(request, "Invalid vote submission. Candidate mismatch.")
            return redirect('student_dashboard')
        
        Vote.objects.create(student=student, candidate=candidate, position=position)
        messages.success(request, 'Vote cast successfully!')
        return redirect('student_dashboard')
        
    return render(request, 'vote.html', {'position': position, 'candidates': candidates})

@login_required
def results(request):
    if not request.user.is_principal(): return redirect('index')
    
    positions = Position.objects.all()
    results_data = []
    
    for position in positions:
        candidates = Candidate.objects.filter(position=position).annotate(total_votes=Count('votes')).order_by('-total_votes')
        
        # Prepare chart data
        labels = [c.student.user.get_full_name() for c in candidates]
        data = [c.total_votes for c in candidates]
        
        results_data.append({
            'position': position,
            'candidates': candidates,
            'chart_labels': json.dumps(labels),
            'chart_data': json.dumps(data),
        })
        
    return render(request, 'results.html', {'results_data': results_data})

@login_required
def election_settings(request):
    if not request.user.is_principal(): return redirect('index')
    settings = ElectionSettings.objects.first()
    
    if request.method == 'POST':
        form = ElectionSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election settings updated.')
            return redirect('principal_dashboard')
    else:
        form = ElectionSettingsForm(instance=settings)
    return render(request, 'form.html', {'form': form, 'title': 'Election Settings'})

@login_required
def add_position(request):
    if not request.user.is_principal(): return redirect('index')
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position added.')
            return redirect('principal_dashboard')
    else:
        form = PositionForm()
    return render(request, 'form.html', {'form': form, 'title': 'Add Position'})

@login_required
def create_broadcast(request):
    if not request.user.is_principal(): return redirect('index')
    if request.method == 'POST':
        form = BroadcastForm(request.POST, request.FILES)
        if form.is_valid():
            broadcast = form.save(commit=False)
            broadcast.created_by = request.user
            broadcast.save()
            messages.success(request, 'Broadcast posted.')
            return redirect('principal_dashboard')
    else:
        form = BroadcastForm()
    return render(request, 'form.html', {'form': form, 'title': 'Post Broadcast'})

def principal_register(request):
    if request.method == 'POST':
        form = PrincipalCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Principal registered and logged in successfully.')
            return redirect('principal_dashboard')
    else:
        form = PrincipalCreationForm()
    return render(request, 'form.html', {'form': form, 'title': 'Register Principal'})

@login_required
def export_results_csv(request):
    if not request.user.is_principal(): return redirect('index')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="election_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Position', 'Candidate', 'Votes'])
    
    positions = Position.objects.all()
    for position in positions:
        candidates = Candidate.objects.filter(position=position).annotate(total_votes=Count('votes')).order_by('-total_votes')
        for candidate in candidates:
            writer.writerow([position.name, candidate.student.user.get_full_name(), candidate.total_votes])
            
    return response

@login_required
def clear_election(request):
    if not request.user.is_principal(): return redirect('index')
    
    if request.method == 'POST':
        Vote.objects.all().delete()
        Candidate.objects.all().delete()
        messages.success(request, 'Election cleared successfully (Votes and Candidates removed).')
        return redirect('principal_dashboard')
        
    return render(request, 'confirm_clear.html', {'title': 'Clear Election'})

@login_required
def delete_teacher(request, teacher_id):
    if not request.user.is_principal(): return redirect('index')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.user.delete()
        messages.success(request, 'Teacher removed.')
    return redirect('principal_dashboard')

@login_required
def delete_student(request, student_id):
    if not request.user.is_principal(): return redirect('index')
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.user.delete()
        messages.success(request, 'Student removed.')
    return redirect('principal_dashboard')

@login_required
def delete_candidate(request, candidate_id):
    if not request.user.is_principal() and not request.user.is_teacher(): return redirect('index')
    candidate = get_object_or_404(Candidate, id=candidate_id)
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, 'Candidate nomination revoked.')
    # Redirect intelligently
    if request.user.is_principal(): return redirect('principal_dashboard')
    if request.user.is_teacher(): return redirect('teacher_dashboard')
    return redirect('index')
