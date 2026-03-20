from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/principal/', views.principal_register, name='principal_register'),
    path('login/teacher/', views.teacher_login, name='teacher_login'),
    path('login/student/', views.student_login, name='student_login'),
    path('logout/', views.user_logout, name='logout'),
    
    path('principal/dashboard/', views.principal_dashboard, name='principal_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-position/', views.add_position, name='add_position'),
    
    path('nominate/', views.nominate_candidate, name='nominate_candidate'),
    path('vote/<int:position_id>/', views.vote_page, name='vote_page'),
    path('results/', views.results, name='results'),
    path('export-results/', views.export_results_csv, name='export_results_csv'),
    path('clear-election/', views.clear_election, name='clear_election'),
    path('settings/', views.election_settings, name='election_settings'),
    path('broadcast/', views.create_broadcast, name='create_broadcast'),
    
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('delete-candidate/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'),
]
