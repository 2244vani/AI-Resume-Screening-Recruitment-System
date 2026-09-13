from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_page, name='logout'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('create-job/', views.create_job, name='create_job'),
    path('match-resume/', views.match_resume, name='match_resume'),
    path('recruiter-dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
path('shortlist/', views.shortlist_candidate, name='shortlist_candidate'),
]