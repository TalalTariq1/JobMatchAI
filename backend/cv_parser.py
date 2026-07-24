import os
from pypdf import PdfReader
from dotenv import load_dotenv
from groq import Groq

# Load environment variables for testing standalone
load_dotenv()

def extract_cv_text(file_path):
    """
    Reads a local PDF file path and extracts all its visible text into a single string.
    """
    reader = PdfReader(file_path)
    extracted_text = ""
    
    # Loop through every page in the PDF and extract text
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
            
    return extracted_text.strip()


def analyze_cv_text(cv_text):
    """
    Sends the raw CV text string to Groq and returns a structured JSON string
    containing the candidate's skills, experience, projects, and personal metadata.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = prompt = f"""
    You are an expert technical talent parser analyzing an engineering resume.
    Your job is to extract a comprehensive JSON profile of the candidate's skills and projects.

    Raw CV Text:
    \"\"\"{cv_text}\"\"\"

    Instructions for Deep Extraction:
    1. DO NOT just look at the 'Technical Skills' section. Read every single project title and bullet point thoroughly.
    2. Under 'skills', extract ALL technologies, languages, frameworks, AND high-level engineering methodologies/disciplines that the candidate explicitly demonstrates or names.
       - If they built full-stack apps, include "Full Stack Development", "Frontend Development", "Backend Development".
       - If they mention building responsive UIs across device sizes, include "Responsive Web Design" or "Responsive Design".
       - If they talk about building RESTful APIs, routing, or connecting services, include "API Integration" and "REST APIs".
    3. Normalize and clean the skills into concise, title-case terms (e.g., "Next.js", "PostgreSQL", "Docker", "FastAPI").
    4. Keep the 'projects' structure clean with 'name' and 'description'.
    5. Under 'contact_info', extract the candidate's full name, email, phone number, GitHub profile URL, LinkedIn profile URL, and GPA, if present anywhere in the text. If a specific field genuinely cannot be found, use an empty string "" for it — never invent or guess a value.
    6. Under 'education', extract the candidate's university/institution name, degree name, and current status (e.g. "In Progress", "Graduated"), if present anywhere in the text. Use an empty string "" for any field genuinely not found.

    Output format MUST be a valid JSON object matching this exact structure with no markdown codeblock wrappers or conversational text:
    {{
        "contact_info": {{
            "name": "Full Name",
            "email": "email@example.com",
            "phone": "+1 234 567 8900",
            "github": "https://github.com/username",
            "linkedin": "https://linkedin.com/in/username",
            "gpa": "3.8"
        }},
        "education": {{
            "institution": "University Name",
            "degree": "Bachelor of Science in Computer Science",
            "status": "In Progress"
        }},
        "skills": ["JavaScript", "TypeScript", "Full Stack Development", "Backend Development", "Responsive Web Design", "API Integration", "Node.js", "Express.js", "MongoDB", "FastAPI", "React.js"],
        "projects": [
            {{"name": "Project Name", "description": "Brief description including stack"}}
        ]
    }}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content


# --- TESTING BLOCK ---
if __name__ == "__main__":
    # Put a real or sample PDF file path here to test it out!
    # Example: Place "my_cv.pdf" in your root folder or backend folder
    TEST_PDF_PATH = "sample_cv.pdf" 
    
    if os.path.exists(TEST_PDF_PATH):
        print(f"--- Step 1: Extracting text from {TEST_PDF_PATH} ---")
        raw_text = extract_cv_text(TEST_PDF_PATH)
        print("Raw text extracted successfully! First 200 characters:")
        print(raw_text[:200] + "...\n")
        
        print("--- Step 2: Sending raw text to Groq for structured analysis ---")
        structured_json = analyze_cv_text(raw_text)
        print("Parsed CV JSON Result:")
        print(structured_json)
    else:
        print(f"To run this test, please drop a sample PDF at: '{TEST_PDF_PATH}' first!")