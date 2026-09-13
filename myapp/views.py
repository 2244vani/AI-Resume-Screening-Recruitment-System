from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail


from .models import Resume, Job, ShortlistedCandidate
from .utils import extract_text_from_pdf, extract_skills
from .matching import calculate_skill_match, calculate_ai_similarity


# ---------------- HOME ----------------

def home(request):
    return render(request, 'home.html')


# ---------------- REGISTER ----------------

def register(request):

    if request.method == 'POST':

        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        return redirect('login')

    return render(request, 'register.html')


# ---------------- LOGIN ----------------

def login_page(request):

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(
            request,
            'login.html',
            {'error': 'Invalid email or password'}
        )

    return render(request, 'login.html')


# ---------------- LOGOUT ----------------

def logout_page(request):
    logout(request)
    return redirect('home')


# ---------------- DASHBOARD ----------------

def dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')

    context = {
        'resumes': resumes,
        'resume_count': resumes.count(),
        'job_count': Job.objects.count(),
        'latest_resume': resumes.first(),
    }

    return render(request, 'dashboard.html', context)


# ---------------- UPLOAD RESUME ----------------

def upload_resume(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':

        resume_file = request.FILES.get('resume')

        if resume_file:

            extracted_text = extract_text_from_pdf(resume_file)
            skills = extract_skills(extracted_text)

            Resume.objects.create(
                user=request.user,
                resume_file=resume_file,
                extracted_text=extracted_text,
                skills=", ".join(skills)
            )

            return redirect('dashboard')

    return render(request, 'upload_resume.html')


# ---------------- CREATE JOB ----------------

def create_job(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':

        Job.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            skills=request.POST['skills']
        )

        return redirect('dashboard')

    return render(request, 'create_job.html')


# ---------------- MATCH RESUME ----------------

def match_resume(request):

    if not request.user.is_authenticated:
        return redirect('login')

    resumes = Resume.objects.filter(user=request.user)
    jobs = Job.objects.all()

    if request.method == 'POST':

        resume = Resume.objects.get(
            id=request.POST.get('resume'),
            user=request.user
        )

        job = Job.objects.get(
            id=request.POST.get('job')
        )

        skill_score, matching_skills = calculate_skill_match(
            resume.skills,
            job.skills
        )

        ai_score = calculate_ai_similarity(
            resume.extracted_text,
            job.description
        )

        return render(
            request,
            'match_result.html',
            {
                'resume': resume,
                'job': job,
                'skill_score': skill_score,
                'ai_score': ai_score,
                'matching_skills': matching_skills,
            }
        )

    return render(
        request,
        'match_resume.html',
        {
            'resumes': resumes,
            'jobs': jobs,
        }
    )


# ---------------- RECRUITER DASHBOARD ----------------

def recruiter_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    jobs = Job.objects.all()

    if request.method == 'POST':

        job = Job.objects.get(id=request.POST.get('job'))
        resumes = Resume.objects.all()

        ranked_candidates = []

        for resume in resumes:

            skill_score, matching_skills = calculate_skill_match(
                resume.skills,
                job.skills
            )

            ai_score = calculate_ai_similarity(
                resume.extracted_text,
                job.description
            )

            ranked_candidates.append({
                'user_id': resume.user.id,
                'candidate': resume.user.first_name,
                'email': resume.user.email,
                'resume_name': resume.resume_file.name,
                'resume_url': resume.resume_file.url,
                'skill_score': skill_score,
                'ai_score': ai_score,
                'matching_skills': matching_skills,
            })

        ranked_candidates.sort(
            key=lambda x: x['ai_score'],
            reverse=True
        )

        return render(
            request,
            'recruiter_result.html',
            {
                'job': job,
                'ranked_candidates': ranked_candidates,
            }
        )

    return render(
        request,
        'recruiter_dashboard.html',
        {'jobs': jobs}
    )


# ---------------- SHORTLIST CANDIDATE ----------------


def shortlist_candidate(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        job_id = request.POST.get('job_id')

        candidate = User.objects.get(id=candidate_id)
        job = Job.objects.get(id=job_id)

        ShortlistedCandidate.objects.get_or_create(
            candidate=candidate,
            job=job
        )

        send_mail(
            subject=f"Congratulations! Shortlisted for {job.title}",
            message=f"""
Hi {candidate.first_name},

Congratulations!

Your resume has been shortlisted for the position of {job.title}.

Our HR team will contact you regarding the next interview round.

Best Regards,
AI Resume Screening Team
""",
            from_email=None,
            recipient_list=[candidate.email],
            fail_silently=False,
        )

        messages.success(request, "Candidate shortlisted successfully!")

    return redirect('recruiter_dashboard')