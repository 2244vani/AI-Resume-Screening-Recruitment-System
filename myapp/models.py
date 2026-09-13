from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ShortlistedCandidate(models.Model):
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    shortlisted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate.email} - {self.job.title}"