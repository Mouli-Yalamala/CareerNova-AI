# CareerNova AI - Multi-Agent Job Application System

CareerNova AI is a comprehensive, open-source system designed to automate and significantly enhance the job application process. It leverages a multi-agent AI pipeline to intelligently parse your resume, scrape real-time job details, analyze your skill gaps, and autonomously generate perfectly tailored application materials—all accessible through a beautiful, modern web interface.

The project is architected with a robust **FastAPI + CrewAI Backend** and a highly responsive **React + Vite Frontend**.

---

## 🚀 Key Features and Workflow

CareerNova AI operates in two distinct phases to ensure high-quality, relevant results while optimizing API and computing costs.

### Phase 1: Research & Analysis
1. **Intelligent Resume Parsing (`Resume Reader` Agent):** 
   Extracts structured candidate profile data (technical/soft skills, work experience, education, total years, and summary) from raw resume text (PDF, DOCX) using tools like `PyPDF2` and `python-docx`.
2. **Job Detail Scraping (`Job Portal Scraper Specialist` Agent):** 
   Automatically fetches and structures job requirements, salary ranges, location, and required experience from job portals based on a user's query using `Serpapi`.
3. **Skill Gap Analysis (`Skills Gap Analysis Expert` Agent):** 
   Compares the candidate's skills against the scraped job requirements using fuzzy matching and NLP. It computes an overall **Match Score (0-100%)**, identifies missing skills, highlights strengths, and generates a personalized learning roadmap.

### 🛡️ The Match Guard Decision Framework
To prevent generating low-quality applications and to save on LLM token costs, CareerNova AI implements a strict **Match Guard**.
*   **If Match Score < 50%:** The pipeline stops after Phase 1. Application materials are **NOT** generated. The system returns the skill gap analysis so the user can focus on building the required skills first.
*   **If Match Score >= 50%:** The profile is considered a viable match, and the system automatically proceeds to Phase 2.

### Phase 2: Generation (Only if Match Score >= 50%)
4. **Tailored Application Materials (`Application Formatter` Agent):** 
   If the matching threshold is met, this agent generates a complete, ATS-optimized application package. This includes:
   *   A highly personalized cover letter.
   *   A structured recruiter outreach email template.
   *   A concise LinkedIn connection message.

---

## 🎨 User Interface (Frontend)

The frontend is built for speed and aesthetics, providing a premium user experience:
*   **Aesthetic:** Features a modern **Dark Mode Glassmorphism** theme.
*   **UX/UI Elements:** Beautiful typography (Inter/Roboto inspired), smooth micro-animations using Framer Motion, and clear, structured presentation of complex JSON data returned by the backend.
*   **Capabilities:** Users can input job queries, upload resumes, and view real-time pipeline execution, ending with actionable insights or ready-to-use application materials.

---

## 🛠️ Technology Stack

### Frontend
*   **Framework:** React 19 + Vite
*   **Styling:** Tailwind CSS V4 (PostCSS)
*   **Icons & Animations:** Lucide React, Framer Motion
*   **HTTP Client:** Axios

### Backend
*   **Framework:** FastAPI + Uvicorn
*   **AI/Agents Framework:** CrewAI (v1.9.3), LiteLLM
*   **Data Processing:** Pandas, NLTK, python-levenshtein
*   **Web Scraping:** Requests, BeautifulSoup4
*   **Document Parsing:** PyPDF2, python-docx

---

## 💻 Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python 3.10+
*   Environment variables set up (API keys for LLMs, e.g., Groq/OpenAI, configured in the backend `.env`).

### 1. Setting up the Backend

1. Navigate to the backend directory:
   ```bash
   cd Backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (create a `.env` file).
5. Run the development server or test the pipeline:
   ```bash
   # Start FastAPI Server (Host: 127.0.0.1, Port: 8000)
   python run.py --dev
   
   # Run pipeline test in CLI
   python run.py --test
   
   # Run pipeline in Mock Mode (No LLM usage)
   python run.py --mock
   ```

### 2. Setting up the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd Frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

The Frontend will be running typically on `http://localhost:5173`. It expects the backend API to be available at `http://localhost:8000`.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check issues page.

## 📄 License
[Add your specific license here, e.g., MIT]
