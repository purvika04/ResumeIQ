import os
import json
from pathlib import Path
import pymupdf
from docx import Document

BASE_DIR = Path(__file__).resolve().parent
RESUMES_DIR = BASE_DIR / "resumes"
JOBS_DIR = BASE_DIR / "jobs"

RESUMES_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)

# 1. JOB DESCRIPTIONS
JOBS = [
    {
        "id": "job-senior-fullstack",
        "title": "Senior Full Stack Engineer",
        "department": "Engineering",
        "location": "Remote / San Francisco",
        "employment_type": "Full-time",
        "min_experience_years": 4.0,
        "required_skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        "preferred_skills": ["AWS", "Redis", "Kubernetes", "CI/CD"],
        "description": "We are looking for an experienced Senior Full Stack Engineer to spearhead core product development. You will design, build, and maintain robust backend microservices with Python and FastAPI, manage high-reliability PostgreSQL databases, and build interactive frontend applications using React and Tailwind CSS. The ideal candidate has strong architectural skills, leverages Docker containerization, and deploys scalable cloud services on AWS."
    },
    {
        "id": "job-nlp-ml-engineer",
        "title": "NLP & Machine Learning Engineer",
        "department": "Artificial Intelligence",
        "location": "New York / Hybrid",
        "employment_type": "Full-time",
        "min_experience_years": 3.0,
        "required_skills": ["Python", "PyTorch", "Natural Language Processing", "Machine Learning", "Transformers"],
        "preferred_skills": ["Scikit-Learn", "Pandas", "spaCy", "LLMs", "HuggingFace"],
        "description": "Join our AI research and development team to build production-grade semantic search, entity extraction pipelines, and transformer ranking engines. You will fine-tune pretrained models, train custom NLP architectures in PyTorch, leverage Hugging Face Transformers, and optimize neural inference pipelines. Requires a strong mathematical foundation in Machine Learning and experience with modern NLP techniques."
    },
    {
        "id": "job-cloud-devops-engineer",
        "title": "Senior Cloud DevOps Engineer",
        "department": "Infrastructure & Platform",
        "location": "Austin / Remote",
        "employment_type": "Full-time",
        "min_experience_years": 4.0,
        "required_skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD"],
        "preferred_skills": ["Linux", "Bash", "GitHub Actions", "Python", "Microservices"],
        "description": "We are seeking a Senior Cloud DevOps Engineer to scale and secure our multi-region cloud infrastructure. You will manage Kubernetes clusters across AWS, define declarative Infrastructure-as-Code using Terraform, automate build and deployment workflows via CI/CD and GitHub Actions, and ensure 99.99% system availability. Extensive knowledge of containerization, Linux systems, and cloud architecture is mandatory."
    }
]

# 2. CANDIDATES DATA
CANDIDATES = [
    {
        "name": "Alex Morgan",
        "email": "alex.morgan.dev@gmail.com",
        "phone": "+1 (415) 882-9104",
        "role": "Senior Full Stack Engineer",
        "exp_years": "2019 - Present",
        "text": """Alex Morgan
Email: alex.morgan.dev@gmail.com | Phone: +1 (415) 882-9104
LinkedIn: https://linkedin.com/in/alexmorgan-dev | GitHub: https://github.com/alexm-dev

Professional Summary
Senior Full Stack Engineer with 5+ years of experience building scalable web architectures and REST APIs. Expert in Python, FastAPI, React, PostgreSQL, and Docker containerization. Proven track record deploying microservices to AWS cloud environments.

Technical Skills
• Languages: Python, JavaScript, TypeScript, SQL, Bash
• Frameworks: FastAPI, Django, React, Next.js, Node.js
• Databases: PostgreSQL, Redis, MongoDB
• Cloud & DevOps: Docker, AWS (EC2, S3), CI/CD, Git, GitHub Actions

Work Experience
Senior Full Stack Developer | Apex Cloud Technologies
2021 - Present (3 years)
• Architected high-throughput REST APIs using Python and FastAPI serving 500k daily requests.
• Developed interactive responsive user dashboards in React and Tailwind CSS.
• Designed and optimized PostgreSQL relational database schemas, reducing query latency by 42%.
• Containerized backend microservices using Docker and orchestrated automated CI/CD pipelines.

Software Engineer | BitWave Solutions
2019 - 2021 (2 years)
• Built core web services in Python and Django with PostgreSQL database integration.
• Implemented client-side features in React and collaborated closely with product managers.

Education
Bachelor of Science in Computer Science
University of California, Berkeley (2015 - 2019)

Certifications
AWS Certified Solutions Architect Associate
""",
        "format": "pdf"
    },
    {
        "name": "Dr. Elena Rostova",
        "email": "elena.rostova.ai@outlook.com",
        "phone": "+1 (617) 492-3301",
        "role": "Lead NLP Research Scientist",
        "exp_years": "2018 - Present",
        "text": """Dr. Elena Rostova
Email: elena.rostova.ai@outlook.com | Phone: +1 (617) 492-3301
LinkedIn: https://linkedin.com/in/elena-rostova-ai | GitHub: https://github.com/erostova-nlp

Professional Summary
AI and NLP Research Specialist with 6 years of experience developing deep learning architectures and language models. Deep expertise in PyTorch, Natural Language Processing, Machine Learning, Transformers, and LLMs.

Technical Skills
• Core AI/ML: Natural Language Processing, Deep Learning, Machine Learning, Computer Vision
• Frameworks: PyTorch, HuggingFace Transformers, Sentence Transformers, spaCy, Scikit-Learn
• Languages: Python, C++, SQL
• Libraries: Pandas, NumPy, Data Visualization, Matplotlib

Work Experience
Lead NLP Engineer | Cognition Labs
2021 - Present (3 years)
• Fine-tuned HuggingFace Transformers and BERT models for cross-lingual document classification.
• Implemented custom attention mechanisms in PyTorch for semantic text ranking and retrieval.
• Preprocessed massive textual corpora using spaCy and Pandas with sub-word tokenization.

Machine Learning Researcher | AI Innovations Lab
2018 - 2021 (3 years)
• Built NLP feature extraction pipelines using Scikit-Learn and PyTorch.
• Trained text embeddings for semantic similarity scoring and recommendation algorithms.

Education
Ph.D. in Computer Science (Artificial Intelligence)
Massachusetts Institute of Technology (2014 - 2018)

Bachelor of Science in Mathematics and Computer Science
Carnegie Mellon University (2010 - 2014)
""",
        "format": "docx"
    },
    {
        "name": "Marcus Vance",
        "email": "marcus.vance.cloud@gmail.com",
        "phone": "+1 (512) 773-4902",
        "role": "Principal Cloud DevOps Engineer",
        "exp_years": "2018 - Present",
        "text": """Marcus Vance
Email: marcus.vance.cloud@gmail.com | Phone: +1 (512) 773-4902
LinkedIn: https://linkedin.com/in/marcus-vance-cloud

Professional Summary
DevOps Architect with 6+ years of experience delivering cloud infrastructure, automated CI/CD pipelines, and Kubernetes container management. Expert in AWS, Docker, Terraform, and Linux administration.

Technical Skills
• Cloud Platforms: AWS, Azure, Google Cloud
• Containers & Orchestration: Kubernetes, Docker, Helm
• Infrastructure as Code: Terraform, Ansible
• CI/CD & Automation: GitHub Actions, Jenkins, CI/CD, Bash scripting
• Languages & OS: Python, Go, Linux, Shell

Work Experience
Senior DevOps Engineer | CloudScale Systems
2021 - Present (3 years)
• Designed and provisioned multi-region AWS cloud infrastructure using Terraform modules.
• Managed production Kubernetes clusters (EKS) hosting 80+ microservices with zero downtime.
• Built end-to-end CI/CD release pipelines with GitHub Actions and Docker image verification.

Cloud Infrastructure Engineer | DataOps Inc.
2018 - 2021 (3 years)
• Automated deployment workflows on AWS with Docker containers and Bash automation.
• Administered Linux Ubuntu and Debian production servers, configuring firewalls and Nginx.

Education
Bachelor of Science in Information Technology
University of Texas at Austin (2014 - 2018)

Certifications
CKA (Certified Kubernetes Administrator)
AWS Certified Solutions Architect Professional
""",
        "format": "pdf"
    },
    {
        "name": "Priya Sharma",
        "email": "priya.sharma.dev@gmail.com",
        "phone": "+1 (408) 555-8812",
        "role": "Full Stack Developer",
        "exp_years": "2021 - Present",
        "text": """Priya Sharma
Email: priya.sharma.dev@gmail.com | Phone: +1 (408) 555-8812
LinkedIn: https://linkedin.com/in/priyasharma-web

Professional Summary
Full Stack Developer with 3 years of hands-on experience in web development using React, Node.js, and Python. Passionate about responsive UI and clean RESTful web services.

Technical Skills
• Frontend: React, JavaScript, HTML5, CSS3, Tailwind CSS, Bootstrap
• Backend: Node.js, Express, Python, REST APIs
• Databases: MongoDB, MySQL
• Tools: Git, GitHub, Agile, Jira

Work Experience
Full Stack Web Developer | Nexa Digital
2021 - Present (3 years)
• Developed single-page web applications with React and Tailwind CSS.
• Implemented REST APIs in Node.js and Python for user authentication and order processing.
• Integrated MongoDB document database collections for flexible product catalog storage.

Education
Bachelor of Science in Computer Science
San Jose State University (2017 - 2021)
""",
        "format": "txt"
    },
    {
        "name": "David Kim",
        "email": "david.kim.eng@gmail.com",
        "phone": "+1 (206) 881-3049",
        "role": "Junior Python Developer",
        "exp_years": "2023 - Present",
        "text": """David Kim
Email: david.kim.eng@gmail.com | Phone: +1 (206) 881-3049
LinkedIn: https://linkedin.com/in/david-kim-python

Professional Summary
Junior Software Developer with 1.5 years of experience in Python programming and backend development. Familiar with Flask, SQLite, and Git version control.

Technical Skills
• Languages: Python, SQL, HTML, CSS
• Web Frameworks: Flask, Django
• Databases: SQLite, MySQL
• Practices: Unit Testing, Git, Object Oriented Programming

Work Experience
Junior Python Developer | Cascade Software
2023 - Present (1.5 years)
• Maintained internal data ingestion scripts in Python.
• Built lightweight CRUD endpoints using Flask with SQLite database.
• Wrote unit testing suites using pytest to ensure code coverage.

Education
Bachelor of Science in Computer Information Systems
University of Washington (2019 - 2023)
""",
        "format": "pdf"
    },
    {
        "name": "Sofia Chen",
        "email": "sofia.chen.ml@gmail.com",
        "phone": "+1 (650) 992-1205",
        "role": "Machine Learning Engineer",
        "exp_years": "2020 - Present",
        "text": """Sofia Chen
Email: sofia.chen.ml@gmail.com | Phone: +1 (650) 992-1205
LinkedIn: https://linkedin.com/in/sofiachen-ml | GitHub: https://github.com/sofiachen-ai

Professional Summary
Machine Learning Engineer with 4 years of experience building predictive models, neural networks, and NLP applications. Skilled in Python, PyTorch, Transformers, and Scikit-Learn.

Technical Skills
• AI & ML: Machine Learning, Deep Learning, Natural Language Processing, Computer Vision
• Libraries: PyTorch, Scikit-Learn, Pandas, NumPy, HuggingFace, Transformers, spaCy
• Languages: Python, SQL, Bash
• Tools: Docker, Git, Linux, Jupyter

Work Experience
Machine Learning Engineer | NeuroTech Solutions
2021 - Present (3 years)
• Built NLP sentiment analysis and entity recognition models using PyTorch and Transformers.
• Implemented feature extraction pipelines with Scikit-Learn and Pandas on tabular and text data.
• Packaged ML inference services into Docker containers for production deployment.

Data Science Associate | Analytic Works
2020 - 2021 (1 year)
• Trained supervised classification algorithms using Scikit-Learn and evaluated ROC-AUC metrics.
• Analyzed large datasets with Pandas and NumPy for customer churn prediction.

Education
Master of Science in Data Science
Stanford University (2018 - 2020)

Bachelor of Science in Statistics
UC Davis (2014 - 2018)
""",
        "format": "docx"
    },
    {
        "name": "Jamal Washington",
        "email": "jamal.washington.devops@gmail.com",
        "phone": "+1 (404) 331-9022",
        "role": "DevOps & Cloud Specialist",
        "exp_years": "2019 - Present",
        "text": """Jamal Washington
Email: jamal.washington.devops@gmail.com | Phone: +1 (404) 331-9022
LinkedIn: https://linkedin.com/in/jamalwashington-devops

Professional Summary
DevOps & Cloud Engineer with 4.5 years of experience deploying reliable cloud environments. Specialized in AWS, Docker, Kubernetes, Terraform, and CI/CD pipelines.

Technical Skills
• Cloud: AWS, Google Cloud
• Containerization: Docker, Kubernetes
• Infrastructure as Code: Terraform
• CI/CD: Jenkins, GitHub Actions, CI/CD
• OS & Scripting: Linux, Bash, Python

Work Experience
DevOps Engineer | Delta Cloud Infrastructure
2021 - Present (3 years)
• Provisioned and secured AWS cloud infrastructure utilizing Terraform scripts.
• Managed high-availability Kubernetes clusters and created automated Helm deployments.
• Maintained CI/CD pipelines in Jenkins and GitHub Actions with automated unit testing.

Systems Administrator | Atlanta Tech Group
2019 - 2021 (2 years)
• Administered Linux enterprise servers and configured network security groups.
• Automated operational maintenance tasks using Python and Bash scripts.

Education
Bachelor of Science in Computer Engineering
Georgia Institute of Technology (2015 - 2019)
""",
        "format": "pdf"
    },
    {
        "name": "Sarah Jenkins",
        "email": "sarah.jenkins.ui@gmail.com",
        "phone": "+1 (312) 880-4491",
        "role": "Senior Frontend Developer",
        "exp_years": "2020 - Present",
        "text": """Sarah Jenkins
Email: sarah.jenkins.ui@gmail.com | Phone: +1 (312) 880-4491
LinkedIn: https://linkedin.com/in/sarahjenkins-frontend

Professional Summary
Senior Frontend Engineer with 3.5 years of experience building responsive, user-centered web applications with React, TypeScript, and Tailwind CSS.

Technical Skills
• Frontend: React, Next.js, Vue, TypeScript, JavaScript, HTML5, CSS3, Tailwind CSS
• Design & UX: Figma, Responsive Design, Web Accessibility
• Tools: Git, Jest, Vite, REST APIs

Work Experience
Lead UI Developer | PixelCraft Studio
2021 - Present (3 years)
• Created modern interactive React single-page applications with Tailwind CSS.
• Implemented reusable component libraries in TypeScript with 98% unit testing coverage.
• Optimized front-end performance, achieving a 99 Lighthouse performance score.

Frontend Developer | Chicago Media Labs
2020 - 2021 (1 year)
• Developed web interfaces in React and JavaScript consuming third-party REST APIs.

Education
Bachelor of Science in Software Engineering
University of Illinois Urbana-Champaign (2016 - 2020)
""",
        "format": "docx"
    },
    {
        "name": "Lucas Silva",
        "email": "lucas.silva.bi@gmail.com",
        "phone": "+1 (786) 441-2099",
        "role": "Business Intelligence & Data Analyst",
        "exp_years": "2021 - Present",
        "text": """Lucas Silva
Email: lucas.silva.bi@gmail.com | Phone: +1 (786) 441-2099
LinkedIn: https://linkedin.com/in/lucassilva-data

Professional Summary
Data Analyst with 2.5 years of experience in data visualization, SQL queries, and business intelligence reporting. Proficient in Tableau, Excel, and Pandas.

Technical Skills
• Analytics: SQL, Data Visualization, Tableau, PowerBI, Excel
• Data Wrangling: Pandas, NumPy, Python basics
• Practices: Agile, Business Reporting

Work Experience
Data Analyst | Coastal Retail Group
2022 - Present (2 years)
• Authored complex SQL queries to extract sales and inventory insights.
• Built executive dashboards in Tableau and PowerBI to monitor revenue KPIs.
• Cleaned and normalized customer data using Python and Pandas.

Education
Bachelor of Science in Economics & Business Analytics
Florida International University (2018 - 2022)
""",
        "format": "txt"
    },
    {
        "name": "Maya Patel",
        "email": "maya.patel.sec@gmail.com",
        "phone": "+1 (703) 662-8190",
        "role": "Information Security & Cybersecurity Analyst",
        "exp_years": "2020 - Present",
        "text": """Maya Patel
Email: maya.patel.sec@gmail.com | Phone: +1 (703) 662-8190
LinkedIn: https://linkedin.com/in/mayapatel-cyber

Professional Summary
Cybersecurity Analyst with 4 years of experience safeguarding networks, conducting penetration testing, and implementing IAM protocols. Familiar with OWASP standards.

Technical Skills
• Security: Cybersecurity, Penetration Testing, OWASP, Cryptography, Network Security, IAM
• Tools: Wireshark, Linux, Splunk, Firewalls
• Compliance: SOC 2, ISO 27001

Work Experience
Cybersecurity Specialist | CyberShield Defense
2021 - Present (3 years)
• Conducted penetration testing and vulnerability assessments following OWASP standards.
• Configured network security firewalls, identity access management (IAM), and encryption.
• Monitored system logs in Splunk to detect and remediate potential security breaches.

Security Analyst | Metro Systems
2020 - 2021 (1 year)
• Performed routine security audits on enterprise Linux servers.

Education
Bachelor of Science in Cybersecurity & Information Assurance
George Mason University (2016 - 2020)
""",
        "format": "pdf"
    },
    {
        "name": "Liam O'Connor",
        "email": "liam.oconnor.backend@gmail.com",
        "phone": "+1 (617) 991-3841",
        "role": "Senior Backend Systems Engineer",
        "exp_years": "2019 - Present",
        "text": """Liam O'Connor
Email: liam.oconnor.backend@gmail.com | Phone: +1 (617) 991-3841
LinkedIn: https://linkedin.com/in/liamoconnor-backend

Professional Summary
Senior Backend Engineer with 4.5 years of experience specializing in high-performance distributed systems, Python, Docker, and PostgreSQL. Experienced in Linux and RESTful services.

Technical Skills
• Languages: Python, Go, SQL, Bash
• Frameworks: FastAPI, Django, REST APIs, Microservices
• Databases: PostgreSQL, Redis
• Cloud & DevOps: Docker, Linux, Git, CI/CD

Work Experience
Senior Backend Engineer | Boston Data Infrastructure
2021 - Present (3 years)
• Designed backend microservices using Python and FastAPI for financial transaction processing.
• Maintained high-throughput PostgreSQL database clusters with connection pooling.
• Dockerized all service applications and integrated automated CI/CD pipelines.

Software Engineer | Commonwealth Systems
2019 - 2021 (2 years)
• Developed REST APIs in Python with PostgreSQL data models.
• Managed Linux deployments and monitored application uptime.

Education
Bachelor of Science in Computer Science
Boston University (2015 - 2019)
""",
        "format": "pdf"
    },
    {
        "name": "Chloe Dubois",
        "email": "chloe.dubois.intern@gmail.com",
        "phone": "+1 (212) 330-9118",
        "role": "AI Research Intern",
        "exp_years": "2025 - 2026",
        "text": """Chloe Dubois
Email: chloe.dubois.intern@gmail.com | Phone: +1 (212) 330-9118
LinkedIn: https://linkedin.com/in/chloedubois-ai

Professional Summary
Recent graduate and AI Research Intern enthusiastic about Machine Learning algorithms and data science. Familiar with Python, Scikit-Learn, and NumPy.

Technical Skills
• Languages: Python, SQL
• Machine Learning: Scikit-Learn, Pandas, NumPy, Machine Learning basics
• Education: High School Diploma, Bachelor of Science in Computer Science candidate

Work Experience
Machine Learning Intern | Horizon AI
2025 - 2026 (6 months)
• Assisted in building baseline classification models with Scikit-Learn.
• Performed data exploration and data visualization using Pandas and Matplotlib.

Education
Bachelor of Science in Computer Science
New York University (Expected Graduation 2026)
""",
        "format": "txt"
    }
]

def generate_pdf(text: str, output_path: Path):
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)  # Standard Letter size
    rect = pymupdf.Rect(40, 40, 572, 752)
    page.insert_textbox(rect, text, fontsize=10, fontname="helv", color=(0.1, 0.1, 0.15))
    doc.save(str(output_path))
    doc.close()

def generate_docx(text: str, output_path: Path):
    doc = Document()
    for line in text.split("\n"):
        clean = line.strip()
        if not clean:
            continue
        if clean in ["Professional Summary", "Technical Skills", "Work Experience", "Education", "Certifications"]:
            doc.add_heading(clean, level=1)
        elif clean.startswith("•"):
            doc.add_paragraph(clean[1:].strip(), style="List Bullet")
        else:
            doc.add_paragraph(clean)
    doc.save(str(output_path))

def main():
    print("Generating synthetic job descriptions...")
    for j in JOBS:
        path = JOBS_DIR / f"{j['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=2)
        print(f"Created job: {path.name}")

    print("\nGenerating synthetic resumes (PDF, DOCX, TXT)...")
    for c in CANDIDATES:
        base_name = c["name"].lower().replace(" ", "_").replace("'", "").replace(".", "")
        fmt = c["format"]
        txt_path = RESUMES_DIR / f"{base_name}.txt"
        
        # Save TXT always for reference
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(c["text"])

        if fmt == "pdf":
            pdf_path = RESUMES_DIR / f"{base_name}.pdf"
            generate_pdf(c["text"], pdf_path)
            print(f"Created PDF: {pdf_path.name}")
        elif fmt == "docx":
            docx_path = RESUMES_DIR / f"{base_name}.docx"
            generate_docx(c["text"], docx_path)
            print(f"Created DOCX: {docx_path.name}")
        else:
            print(f"Created TXT: {txt_path.name}")

    print("\nSample dataset generation completed successfully!")

if __name__ == "__main__":
    main()
