# AI Resume Analyzer

> 🚀 A polished Flask app that turns PDF resumes into actionable career insights using OpenAI.

![Resume Analysis](https://img.shields.io/badge/Flask-application-blue?style=for-the-badge&logo=flask)
![OpenAI](https://img.shields.io/badge/OpenAI-AI%20Driven-orange?style=for-the-badge&logo=openai)

---

## ✨ What it does

AI Resume Analyzer helps job seekers review their resumes instantly. Upload a PDF, choose the review options, and get back:

- a resume quality score
- strengths and weaknesses
- targeted improvement suggestions
- extracted technical and soft skills
- optional job description match feedback

The app is ideal for testing resume polish before applying to roles.

## 🚀 Highlights

- Simple drag-and-drop resume upload flow
- Clean web interface with instant analysis
- OpenAI-powered guidance for modern resumes
- Job description alignment for targeted applications
- PDF-only processing for consistent output
- Mock fallback when OpenAI is unavailable

## 🧩 Built with

- Python 3.9+
- Flask
- PyPDF2
- OpenAI Python SDK
- python-dotenv

## 📦 Installation

1. Open the project directory.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install the required packages:

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET=your_secret_key_here
```

## ▶️ Run locally

```powershell
python app.py
```

Then visit:

```text
http://127.0.0.1:5000
```

## 📝 How to use

1. Upload your PDF resume.
2. Choose the review options you want.
3. Optionally paste a target job description.
4. Submit and review the generated feedback.

## 📁 Project structure

- `app.py` — main Flask application and OpenAI integration
- `requirements.txt` — dependency list
- `templates/index.html` — user interface template
- `static/style.css` — page styling
- `uploads/` — saved resume uploads

## 💡 Notes

- Only PDF uploads are accepted.
- If OpenAI API access is unavailable, the app falls back to a mock analysis path.
- Use `FLASK_SECRET` in `.env` to secure session features.

## 🛠️ Customization tips

- Update `templates/index.html` to modify the form UI.
- Use custom OpenAI prompts in `app.py` to change analysis style.
- Add new analysis sections or scoring rules easily in the review functions.

## 📢 Want to improve this project?

- Add resume parsing for DOCX uploads
- Add history tracking for analyzed resumes
- Add email export or downloadable reports

---

## 📌 License

No license has been added yet. Add one before publishing or open sourcing this project.
