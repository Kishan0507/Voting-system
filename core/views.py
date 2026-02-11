import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from .forms_new import (
    PrincipalLoginForm, TeacherLoginForm, StudentLoginForm,
    TeacherCreationForm, StudentCreationForm, PositionForm,
    CandidateNominationForm, BroadcastForm, ElectionSettingsForm
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
    return render(request, 'index.html')

def principal_login(request):
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
    students_count = Student.objects.count()
    candidates_count = Candidate.objects.count()
    votes_count = Vote.objects.count()
    broadcasts = Broadcast.objects.all().order_by('-created_at')
    
    election_settings = ElectionSettings.objects.first()
    
    context = {
        'teachers': teachers,
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
    
    context = {
        'teacher': teacher,
        'students': students,
        'nominated_candidates': nominated_candidates,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def student_dashboard(request):
    if not request.user.is_student(): return redirect('index')
    
    student = request.user.student_profile
    positions = Position.objects.all()
    # Check which positions the student has voted for
    voted_positions = list(Vote.objects.filter(student=student).values_list('position_id', flat=True))
    
    context = {
        'student': student,
        'positions': positions,
        'voted_positions': voted_positions,
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
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully')
            return redirect('teacher_dashboard') if request.user.is_teacher() else redirect('principal_dashboard')
    else:
        form = StudentCreationForm()
    return render(request, 'form.html', {'form': form, 'title': 'Add Student'})

@login_required
def nominate_candidate(request):
    if not request.user.is_teacher(): return redirect('index')
    if request.method == 'POST':
        form = CandidateNominationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check for existing nomination
            aadhaar = form.cleaned_data['student_aadhaar']
            student = Student.objects.get(aadhaar=aadhaar)
            position = form.cleaned_data['position']
            
            if Candidate.objects.filter(student=student, position=position).exists():
                messages.error(request, 'This student is already nominated for this position.')
            else:
                candidate = form.save(commit=False)
                candidate.student = student
                candidate.nominated_by = request.user.teacher_profile
                candidate.save()
                messages.success(request, 'Candidate nominated successfully')
                return redirect('teacher_dashboard')
    else:
        form = CandidateNominationForm()
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
