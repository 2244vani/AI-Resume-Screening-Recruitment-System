from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_skill_match(resume_skills, job_skills):

    resume_skills = {
        skill.strip().lower()
        for skill in resume_skills.split(",")
        if skill.strip()
    }

    job_skills = {
        skill.strip().lower()
        for skill in job_skills.split(",")
        if skill.strip()
    }

    if not job_skills:
        return 0, []

    matching_skills = resume_skills.intersection(job_skills)

    score = (len(matching_skills) / len(job_skills)) * 100

    return round(score, 2), sorted(matching_skills)


def calculate_ai_similarity(resume_text, job_description):

    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(similarity * 100, 2)