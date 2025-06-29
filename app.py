import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pdfplumber
import docx

# ----------------- Core Functions ---------------------
def calculate_match_score(resume_text, job_text):
    texts = [resume_text, job_text]
    tfidf = TfidfVectorizer(stop_words='english')
    vectorized = tfidf.fit_transform(texts)
    score = cosine_similarity(vectorized[0:1], vectorized[1:2])
    return round(score[0][0] * 100)

def extract_keywords(text):
    text = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    VALID_SKILLS = {
        "python", "java", "c++", "javascript", "html", "css",
        "pandas", "numpy", "tensorflow", "scikit", "sklearn",
        "matplotlib", "seaborn", "mysql", "mongodb", "react",
        "flask", "django", "streamlit", "fastapi", "aws", "azure",
        "git", "github", "docker", "kubernetes", "nlp", "bert",
        "data", "model", "machine", "learning", "analysis"
    }
    return set(word for word in text if word in VALID_SKILLS)

# ----------------- Page Setup ---------------------
st.set_page_config(
    page_title="Resume Match Analyzer",
    page_icon="🧠",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #0e4500, #020500);
}
h1, h2, h3 {
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.stFileUploader {
    background-color: #0d1f06;
    font-color: #000000;
    border: 2px #4CAF50;
    padding: 10px;
    border-radius: 12px;
    transition: all 0.3s ease;
}
.stFileUploader:hover {
    border-color: #2e7d32;
    background-color: #0c360a;
}
.stTextArea > div > textarea {
    background-color: #8f8f8f;
    border: 1.5px solid #4CAF50;
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
    transition: 0.3s ease-in-out;
}
.stTextArea > div > textarea:focus {
    border-color: #2e7d32;
    background-color: #f0fff4;
}
label, .css-1cpxqw2 {
    color: #1e4620;
    font-weight: bold;
}
.stButton button {
    background-color: #4CAF50;
    color: white;
    font-size: 16px;
    border-radius: 8px;
    padding: 10px 24px;
    transition: 0.3s ease-in-out;
}
.stButton button:hover {
    background-color: #45a049;
}
.skill-tag {
    background-color: #ffe0e0;
    color: #b30000;
    padding: 6px 12px;
    border-radius: 15px;
    display: inline-block;
    margin: 5px 5px 0 0;
    font-size: 15px;
    animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity: 1;}
}
</style>
""", unsafe_allow_html=True)

# ----------------- Title Section ---------------------
col1, col2 = st.columns([4, 1])  # Wider title, smaller image

with col1:
    st.markdown("""
        <div style='text-align: left; padding: 10px 0 30px 0'>
            <h1 style='font-size: 38px;'>📄 Resume vs Job Description Matcher</h1>
            <p style='font-size: 21px; color: #cfcfcf;'>Find how well your resume aligns with a job role</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.image("undraw_success_288d.png", use_container_width=True)

# ----------------- File Reader ---------------------
def read_file(file):
    file_type = file.type
    if file_type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode("utf-8")

# ----------------- Inputs Section ---------------------
st.markdown("### 📥 Upload & Input Section")
left, right = st.columns(2)

with left:
    st.subheader("Upload Your Resume")
    resume_file = st.file_uploader("Upload a .txt/.pdf/.docx file", type=["txt", "pdf", "docx"], key="resume")
    if resume_file:
        st.success(" Resume uploaded!")



with right:
    st.subheader("Job Description")
    job_file = st.file_uploader("Upload a .txt/.pdf/.docx file", type=["txt", "pdf", "docx"], key="jobdesc")
    job_text = st.text_area("Or paste job description text here", height=280)
    if job_file:
        st.success(" Job Description uploaded!")
    elif job_text.strip():
        st.success(" Job Description text entered!")


# ----------------- Button Logic ---------------------
if st.button("🔍 Analyze Match"):
    st.markdown("<hr>", unsafe_allow_html=True)

    if resume_file and (job_file or job_text.strip()):
        with st.spinner("Analyzing...Please wait!"):
            resume_text = read_file(resume_file)
            if job_file:
                job_text = read_file(job_file)
            else:
                job_text = job_text.strip()

            match_score = calculate_match_score(resume_text, job_text)

        # ---------- Score Display ----------
        st.markdown("### Match Score")
        color = "#4CAF50" if match_score >= 70 else "#FFA500" if match_score >= 40 else "#FF4444"
        st.markdown(f"""
        <div style='text-align: center; font-size: 36px; font-weight: bold; color: {color}; padding: 10px 0'>
            {match_score}%
        </div>
        """, unsafe_allow_html=True)

        # ---------- Expanders ----------
        with st.expander("📄 View Resume Text"):
            st.write(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
        with st.expander("📝 View Job Description Text"):
            st.write(job_text)

        # ---------- Skill Analysis ----------
        st.markdown("### 🧠 Suggestions to Improve Your Resume")
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(job_text)
        missing_keywords = jd_keywords - resume_keywords

        if missing_keywords:
            st.markdown("Your resume is missing the following relevant skills:")
            for skill in sorted(missing_keywords):
                st.markdown(f"<span class='skill-tag'>{skill}</span>", unsafe_allow_html=True)
        else:
            st.success(" Great! Your resume covers all relevant skills!")
    else:
        st.warning("Please upload a resume and either upload or paste a job description.")

# ----------------- Footer ---------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; color: #888;'>Built with ❤️ using Streamlit · By Nisha</p>", unsafe_allow_html=True)
