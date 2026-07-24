import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def parse_job_description(sample_job_text):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = f"""
    You are an elite automated talent acquisition system parsing raw job descriptions.
    Your objective is to extract all hiring criteria and structural technical requirements into a strict JSON structure.

    Raw Job Description Text:
    \"\"\"{sample_job_text}\"\"\"

    Extraction Rules:
    1. SCAN EVERYTHING: Technical requirements can be hidden anywhere—inside 'Responsibilities', 'Requirements', 'Preferred Skills', or the opening 'Job Summary'. Scan the entire text.
    2. 'job_title': Extract the specific job title being hired for. It may be explicitly labeled, or it may only appear in the opening sentence (e.g. "seeking a skilled WordPress/Front-End Developer" means the job_title is "WordPress/Front-End Developer"). If genuinely no title can be determined, use "".
    3. 'tech_stack': Extract concrete programming languages, databases, frameworks, libraries, developer tools, and infrastructure (e.g., React.js, DotNet, TypeScript, Node.js, MongoDB, WordPress, WooCommerce, Tailwind CSS, Git, Docker, JWT).
    4. 'key_skills': Extract high-level engineering disciplines, methodologies, or technical conceptual concepts (e.g., Backend Development, Frontend Development, Full Stack Development, API Integration, Responsive Web Design, SEO Optimization, UI/UX Conversion, Browser Debugging).
    5. FILTER OUT SOFT SKILLS: Completely ignore generic human traits like "motivated", "willingness to learn", "communication", "problem-solving", "team player", "analytical skills", "independent".
    6. FILTER OUT METADATA: Do not extract salary details, shift timings, degree names, or office locations into these arrays.

    Output format MUST be a valid JSON object matching this exact structure with no conversational text or backticks:
    {{
        "job_title": "Frontend Developer",
        "key_skills": ["Frontend Development", "Responsive Web Design", "API Integration"],
        "tech_stack": ["React.js", "Next.js", "Tailwind CSS", "Git"]
    }}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1 # Low temperature ensures strict data extraction without creativity
    )
    
    return response.choices[0].message.content.strip()



if __name__ == "__main__":
    
    # 1. A fake job description to test with
    sample_jd = """
    Full job description
Job description
We are seeking a skilled WordPress/Front-End Developer to join our team and help us develop and maintain a variety of web-based applications.
The ideal candidate will have experience in building user-friendly and SEO friendly interactive websites using modern web development technologies.

Responsibilities:

Experience in JavaScript, CSS and jQuery Hands on experience with html5, CSS3, TAILWIND CSS Experience in css3 animation, css3 transform, CSS Media Queries, and flex.
Familiarity with Frameworks and Libraries like bootstrap version 3 to 5, AngularJS, Ember and ReactJS.
Familiarity and Experience with different Open sources especially in (Word Press + woo commerce) and any content management systems Familiarity with software like Adobe Suite, Photoshop, Illustrator Ability to test and debug websites Familiarity with browser testing and debugging Advanced problem-solving skills required.
Experience of Fixing any website issues or bugs that arise Creating pixel perfect websites for desktop and mobile via Word Press
Creating landing pages and forms that get our clients leads and sales (HTML & CSS) Editing Word Press themes to be 20% more awesome Dealing with random hosting,
DNS, and website issues that pop up Ability to operate Photoshop and Illustrator at a basic level (to translate PSD and AI designs into HTML & Word Press) Building UI’s to specifications based on provided PSD mockups Implementing 3rd-party libraries and basic APIs Social media API experience Google Maps API experience
Requirements:
Bachelor's/Masters degree in Computer Science or related field
2-3 years of experience in the related field
Job Type: Full-time (On-site)
Salary: Rs30,000. – Rs40,000. per month
Location: Gulshan-e-Iqbal Karachi

Pay: Rs30,000.00 - Rs40,000.00 per month

Education:

Bachelor's (Preferred)
Work Location: In person




    """
    
    print("Sending JD to Groq...\n")
    
    # 2. Run the function
    result = parse_job_description(sample_jd)
    
    # 3. Print the JSON output
    print("Parsed JSON Result:")
    print(result)