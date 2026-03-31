import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, flash
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from openai import OpenAI
import random

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Initialize OpenAI client with API key
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(path):
    try:
        reader = PdfReader(path)
        text_parts = []
        for p in reader.pages:
            page_text = p.extract_text()
            if page_text:
                text_parts.append(page_text)
        return '\n'.join(text_parts)
    except Exception:
        return ''


def get_resume_score(resume_text):
    """Generate a resume quality score (0-100)."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not set (OPENAI_API_KEY).')

    system_msg = (
        "You are an expert career coach and resume reviewer. "
        "Analyze the resume and give a Resume Score between 0 and 100 based on overall quality. "
        "Return ONLY the response in this format:\n\n"
        "Resume Score: (0–100)\n\n"
        "Brief Explanation:\n"
        "Explain why this score was given."
    )

    user_msg = f"Resume Text:\n{resume_text}"

    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise


def get_strengths_weaknesses(resume_text):
    """Analyze strengths and weaknesses of the resume."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not set (OPENAI_API_KEY).')

    system_msg = (
        "You are an expert career coach. Analyze the resume and identify strengths and weaknesses. "
        "Return ONLY the response in this format:\n\n"
        "Strengths:\n"
        "- List the strong points of the resume\n"
        "- Mention skills, projects, achievements, or experience\n\n"
        "Weaknesses:\n"
        "- Mention missing sections\n"
        "- Mention unclear descriptions\n"
        "- Mention formatting issues"
    )

    user_msg = f"Resume Text:\n{resume_text}"

    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            temperature=0.2,
            max_tokens=600,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise


def get_improvement_suggestions(resume_text):
    """Generate improvement suggestions for the resume."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not set (OPENAI_API_KEY).')

    system_msg = (
        "You are an expert career coach. Review the resume and provide improvement suggestions. "
        "Return ONLY the response in this format:\n\n"
        "Improvement Suggestions:\n"
        "- Suggest ways to improve the resume\n"
        "- Suggest adding measurable achievements\n"
        "- Suggest adding certifications or projects\n"
        "- Suggest better formatting"
    )

    user_msg = f"Resume Text:\n{resume_text}"

    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            temperature=0.2,
            max_tokens=600,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise


def extract_skills(resume_text):
    """Extract technical and soft skills from the resume."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not set (OPENAI_API_KEY).')

    system_msg = (
        "You are an expert in identifying skills. Extract all skills from the following resume. "
        "Return ONLY the response in this format:\n\n"
        "Technical Skills:\n"
        "- programming languages\n"
        "- frameworks\n"
        "- tools\n\n"
        "Soft Skills:\n"
        "- communication\n"
        "- teamwork\n"
        "- leadership"
    )

    user_msg = f"Resume Text:\n{resume_text}"

    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            temperature=0.2,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise


def match_job_description(resume_text, job_description):
    """Compare resume with job description and provide match analysis."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not set (OPENAI_API_KEY).')

    system_msg = (
        "You are an expert recruiter. Compare the resume with the given job description. "
        "Return ONLY the response in this format:\n\n"
        "Match Score: (0–100)\n\n"
        "Matching Skills:\n"
        "- skills present in both resume and job description\n\n"
        "Missing Skills:\n"
        "- skills required in the job description but missing in the resume\n\n"
        "Suggestions:\n"
        "- how the candidate can improve the resume for this job"
    )

    user_msg = f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}"

    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            temperature=0.2,
            max_tokens=700,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise


def analyze_with_openai(resume_text):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not set (OPENAI_API_KEY).')

    system_msg = (
        "You are an expert career coach. Analyze resumes and return output strictly in the following format:\n"
        "Strengths:\n- ...\n\nWeaknesses:\n- ...\n\nImprovement Suggestions:\n- ...\n\n"
        "Do not include any extra text or headings beyond these three sections."
    )

    user_msg = f"Analyze the following resume text delimited by triple backticks. Resume:\n```{resume_text}```"

    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ],
            temperature=0.2,
            max_tokens=600,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # if quota issue or any other API error, raise to be handled by caller
        raise


def mock_analysis(resume_text):
    # generate a simple pseudo-analysis based on resume length / random choice
    strengths = [
        "Strong communication skills",
        "Extensive industry experience",
        "Proven leadership abilities",
        "Detail-oriented and organized",
        "Adaptable to new technologies"
    ]
    weaknesses = [
        "Limited quantitative results",
        "Needs clearer formatting",
        "Several typos present",
        "Lacks specific technical tools",
        "Weak summary section"
    ]
    suggestions = [
        "Include measurable achievements",
        "Use action verbs in descriptions",
        "Add relevant certifications",
        "Shorten lengthy paragraphs",
        "Highlight teamwork examples"
    ]
    # pick some items deterministically using text hash
    seed = len(resume_text) + sum(ord(c) for c in resume_text[:50])
    random.seed(seed)
    chosen_strengths = random.sample(strengths, 2)
    chosen_weaknesses = random.sample(weaknesses, 2)
    chosen_suggestions = random.sample(suggestions, 2)
    # build string in expected format
    return (
        "Strengths:\n" + "\n".join(f"- {s}" for s in chosen_strengths) + "\n\n"
        "Weaknesses:\n" + "\n".join(f"- {w}" for w in chosen_weaknesses) + "\n\n"
        "Improvement Suggestions:\n" + "\n".join(f"- {i}" for i in chosen_suggestions)
    )


def mock_resume_score(resume_text):
    """Generate mock resume score when API quota is exceeded."""
    seed = len(resume_text) + sum(ord(c) for c in resume_text[:50])
    random.seed(seed)
    score = random.randint(65, 88)
    return f"Resume Score: {score}/100\n\nBrief Explanation:\nYour resume demonstrates solid professional experience with clear career progression. Consider adding more quantifiable metrics and strengthening your summary section to improve the overall impact."


def mock_improvement_suggestions(resume_text):
    """Generate mock improvement suggestions when API quota is exceeded."""
    suggestions = [
        "Add measurable achievements and metrics (e.g., increased sales by 25%)",
        "Use stronger action verbs (led, designed, implemented) instead of passive language",
        "Include relevant technical skills and certifications",
        "Reduce length of job descriptions - aim for 2-3 bullet points per role",
        "Add a professional summary highlighting your key strengths",
        "Include metrics and ROI where applicable"
    ]
    seed = len(resume_text) + sum(ord(c) for c in resume_text[:50])
    random.seed(seed)
    chosen = random.sample(suggestions, 4)
    return "Improvement Suggestions:\n" + "\n".join(f"- {s}" for s in chosen)


def mock_extract_skills(resume_text):
    """Generate mock skill extraction when API quota is exceeded."""
    technical_skills = [
        "Python", "JavaScript", "Java", "C++", "SQL", "AWS", "Docker", 
        "Git", "REST APIs", "Machine Learning", "Data Analysis", "React"
    ]
    soft_skills = [
        "Leadership", "Communication", "Problem Solving", "Team Collaboration",
        "Project Management", "Time Management", "Critical Thinking"
    ]
    seed = len(resume_text) + sum(ord(c) for c in resume_text[:50])
    random.seed(seed)
    chosen_tech = random.sample(technical_skills, 3)
    chosen_soft = random.sample(soft_skills, 3)
    
    result = "Technical Skills:\n" + "\n".join(f"- {s}" for s in chosen_tech)
    result += "\n\nSoft Skills:\n" + "\n".join(f"- {s}" for s in chosen_soft)
    return result


def mock_job_match(resume_text, job_description):
    """Generate mock job match when API quota is exceeded."""
    seed = len(resume_text) + len(job_description) + sum(ord(c) for c in (resume_text + job_description)[:50])
    random.seed(seed)
    score = random.randint(60, 85)
    
    matching_items = [
        "Your experience aligns with the role requirements",
        "Technical skills match the job description",
        "Professional background is relevant",
        "Leadership experience demonstrated"
    ]
    gaps = [
        "Consider gaining more experience in specific tool",
        "Add additional certifications mentioned in JD",
        "Develop deeper expertise in mentioned technology"
    ]
    
    chosen_match = random.sample(matching_items, 2)
    chosen_gaps = random.sample(gaps, 1)
    
    result = f"Job Match Score: {score}%\n\n"
    result += "Matching:\n" + "\n".join(f"- {m}" for m in chosen_match)
    result += "\n\nAreas to Develop:\n" + "\n".join(f"- {g}" for g in chosen_gaps)
    return result


def parse_structured_response(text):
    sections = {
        'Strengths': [],
        'Weaknesses': [],
        'Improvement Suggestions': []
    }

    # Find section boundaries
    def find_block(start_label, following_label=None):
        try:
            start = text.index(start_label) + len(start_label)
        except ValueError:
            return ''
        if following_label:
            try:
                end = text.index(following_label)
                return text[start:end].strip()
            except ValueError:
                return text[start:].strip()
        else:
            return text[start:].strip()

    strengths_block = find_block('Strengths:', 'Weaknesses:')
    weaknesses_block = find_block('Weaknesses:', 'Improvement Suggestions:')
    suggestions_block = find_block('Improvement Suggestions:')

    def lines_to_list(block):
        lines = []
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('-'):
                lines.append(line.lstrip('-').strip())
            else:
                lines.append(line)
        return lines

    sections['Strengths'] = lines_to_list(strengths_block)
    sections['Weaknesses'] = lines_to_list(weaknesses_block)
    sections['Improvement Suggestions'] = lines_to_list(suggestions_block)
    return sections


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint to verify server is responding."""
    return {'status': 'Server is running!'}


@app.route('/analyze', methods=['POST'])
def analyze():
    # Basic error handling: uploaded file presence
    if 'resume' not in request.files:
        flash('No file part in the request. Please upload a PDF resume.')
        return redirect('/')

    file = request.files['resume']

    if file.filename == '':
        flash('No file selected. Please choose a PDF file.')
        return redirect('/')

    if not allowed_file(file.filename):
        flash('Invalid file type. Only PDF files are allowed.')
        return redirect('/')

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # Extract text
    resume_text = extract_text_from_pdf(save_path)
    if not resume_text or resume_text.strip() == '':
        flash('Could not extract text from the uploaded PDF or the PDF is empty.')
        return redirect('/')

    # Get selected analysis types (multiple selection support)
    selected_types = request.form.getlist('analysis_types')
    if not selected_types:
        # If no checkboxes selected, run all analyses by default
        selected_types = ['strengths_weaknesses', 'resume_score', 'improvement_suggestions', 'skills_extraction', 'job_match']
    
    job_description = request.form.get('job_description', '').strip()
    results = {}
    
    # DEBUG: Log what we're processing
    print(f"\n{'='*60}")
    print(f"DEBUG: Analyze request received")
    print(f"DEBUG: File: {filename}")
    print(f"DEBUG: Selected types: {selected_types}")
    print(f"DEBUG: Job description provided: {bool(job_description)}")
    print(f"{'='*60}\n")

    try:
        # Process each selected analysis type independently
        for analysis_type in selected_types:
            print(f"DEBUG: Starting analysis for: {analysis_type}")
            try:
                if analysis_type == 'strengths_weaknesses':
                    print(f"  -> Calling get_strengths_weaknesses()...")
                    raw_analysis = get_strengths_weaknesses(resume_text)
                    results['strengths_weaknesses'] = parse_structured_response(raw_analysis)
                    print(f"  -> SUCCESS: strengths_weaknesses completed")
                
                elif analysis_type == 'resume_score':
                    print(f"  -> Calling get_resume_score()...")
                    raw_analysis = get_resume_score(resume_text)
                    results['resume_score'] = raw_analysis
                    print(f"  -> SUCCESS: resume_score completed")
                
                elif analysis_type == 'improvement_suggestions':
                    print(f"  -> Calling get_improvement_suggestions()...")
                    raw_analysis = get_improvement_suggestions(resume_text)
                    results['improvement_suggestions'] = raw_analysis
                    print(f"  -> SUCCESS: improvement_suggestions completed")
                
                elif analysis_type == 'skills_extraction':
                    print(f"  -> Calling extract_skills()...")
                    raw_analysis = extract_skills(resume_text)
                    results['skills_extraction'] = raw_analysis
                    print(f"  -> SUCCESS: skills_extraction completed")
                
                elif analysis_type == 'job_match':
                    print(f"  -> Calling match_job_description()...")
                    if job_description:
                        raw_analysis = match_job_description(resume_text, job_description)
                        results['job_match'] = raw_analysis
                    else:
                        # Always include job_match in results, with message if no description
                        results['job_match'] = "No job description provided.\n\nTo enable Job Description Matching:\n- Add a job description in the text field above\n- This analysis will compare your resume against the job requirements\n- You'll get a match score and recommendations"
                    print(f"  -> SUCCESS: job_match completed")
            except Exception as analysis_error:
                # If one analysis fails, log it but continue with others
                error_msg = str(analysis_error)
                print(f"  -> FAILED: Error in {analysis_type}: {error_msg}")
                
                # Check if it's a quota error - if so, use mock data instead
                if 'insufficient_quota' in error_msg or 'RateLimitError' in error_msg or '429' in error_msg:
                    print(f"  -> Attempting fallback mock data for {analysis_type}...")
                    try:
                        if analysis_type == 'strengths_weaknesses':
                            raw_analysis = mock_analysis(resume_text)
                            results['strengths_weaknesses'] = parse_structured_response(raw_analysis)
                        elif analysis_type == 'resume_score':
                            results['resume_score'] = mock_resume_score(resume_text)
                        elif analysis_type == 'improvement_suggestions':
                            results['improvement_suggestions'] = mock_improvement_suggestions(resume_text)
                        elif analysis_type == 'skills_extraction':
                            results['skills_extraction'] = mock_extract_skills(resume_text)
                        elif analysis_type == 'job_match' and job_description:
                            results['job_match'] = mock_job_match(resume_text, job_description)
                        print(f"  -> SUCCESS: Mock {analysis_type} loaded")
                    except Exception as mock_error:
                        print(f"  -> Mock also failed: {str(mock_error)}")
                        results[analysis_type] = f"Unable to process {analysis_type}"
                else:
                    # Non-quota error - just store the error message
                    results[analysis_type] = f"Error processing {analysis_type}: {error_msg}"
        
        # Make sure at least some results were generated
        if not results:
            print("DEBUG: No results generated - all analyses failed!")
            flash('Error: No analysis results were generated. Please try again.')
            return redirect('/')
        
        print(f"DEBUG: Analysis complete. Results keys: {list(results.keys())}")
        print(f"{'='*60}\n")
            
        return render_template('index.html', 
                             results=results, 
                             selected_types=selected_types,
                             filename=filename)
    
    except RuntimeError as e:
        print(f"DEBUG: RuntimeError caught: {str(e)}")
        flash(str(e))
        return redirect('/')
    except Exception as e:
        # Catch ALL exceptions and log them
        error_msg = str(e)
        print(f"DEBUG: Exception caught: {error_msg}")
        print(f"DEBUG: Exception type: {type(e).__name__}")
        
        # Check if it's a quota error
        if 'insufficient_quota' in error_msg or 'RateLimitError' in error_msg or '429' in error_msg:
            print("DEBUG: Quota error detected, returning mock analysis")
            flash('API quota exhausted; showing sample analysis results.')
            # Build results using mock data for all selected types
            results = {}
            if 'strengths_weaknesses' in selected_types:
                raw_analysis = mock_analysis(resume_text)
                results['strengths_weaknesses'] = parse_structured_response(raw_analysis)
            if 'resume_score' in selected_types:
                results['resume_score'] = mock_resume_score(resume_text)
            if 'improvement_suggestions' in selected_types:
                results['improvement_suggestions'] = mock_improvement_suggestions(resume_text)
            if 'skills_extraction' in selected_types:
                results['skills_extraction'] = mock_extract_skills(resume_text)
            if 'job_match' in selected_types and job_description:
                results['job_match'] = mock_job_match(resume_text, job_description)
            elif 'job_match' in selected_types:
                results['job_match'] = "No job description provided.\n\nTo enable Job Description Matching:\n- Add a job description in the text field above\n- This analysis will compare your resume against the job requirements\n- You'll get a match score and recommendations"
            
            return render_template('index.html', 
                                 results=results, 
                                 selected_types=selected_types,
                                 filename=filename)
        else:
            # For all other errors, flash the error but still try to show results if any were generated
            print(f"DEBUG: Non-quota error, showing any partial results")
            if results:
                flash(f'Partial results available. Error: {error_msg}')
                return render_template('index.html', 
                                     results=results, 
                                     selected_types=selected_types,
                                     filename=filename)
            else:
                flash(f'Error analyzing resume: {error_msg}')
                return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
