from app.config.settings import get_settings
settings = get_settings()
SECTION_KEYWORDS = {
    "aboutMe": ["about", "introduce", "who are you", "summary", "profile"],
    
    "personalInfo": [
        "name", "full name", "your name",
        "contact", "email", "phone", "location",
        "linkedin", "github", "portfolio"
    ],
    "educations": ["education", "college", "degree", "bca", "study", "qualification"],
    "experience": ["experience", "work", "working", "company", "job", "career"],
    "skills": ["skill", "skills", "technology", "tech", "stack", "programming", "development", "framework", "language"],
    "certifications": ["certificate", "certification", "certified"],
    "achievements":["achievement", "accomplishment"]
}
TOP_K = 3
VECTOR_K = 15

SEARCH_FALL_BACK_ANSWER = (
    "⚠️ I couldn't find any data for this profile.\n\n"
    "Please check if the **chat ID is correct** or try a different query.\n\n"
    f"👉 Visit this website to create Chat ID: {settings.FRONTEND_URL}"
)
