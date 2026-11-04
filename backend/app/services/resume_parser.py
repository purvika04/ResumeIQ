import re
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pymupdf
fitz = pymupdf
from docx import Document

from app.schemas.resume import (
    ParsedResumeData,
    EducationItem,
    WorkExperienceItem,
    ProjectItem,
    SkillItem,
)
from app.services.skill_extractor import skill_extractor

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?"
)
LINKEDIN_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/([a-zA-Z0-9_-]+)", re.IGNORECASE
)
GITHUB_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)", re.IGNORECASE
)

SECTION_HEADERS = {
    "summary": [
        "summary", "professional summary", "profile", "about me", "career objective",
        "objective", "executive summary", "overview"
    ],
    "experience": [
        "experience", "work experience", "employment history", "professional experience",
        "work history", "career history", "relevant experience"
    ],
    "education": [
        "education", "academic background", "academic qualifications", "education and credentials",
        "academic history", "educational qualifications"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "skills & competencies",
        "technologies", "tech stack", "tools & technologies", "skills & tools"
    ],
    "projects": [
        "projects", "key projects", "personal projects", "academic projects",
        "technical projects", "featured projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses & certifications", "credentials",
        "professional certifications"
    ]
}

DEGREE_PATTERNS = [
    (r"\b(?:Ph\.?D\.?|Doctor of Philosophy)\b", "Ph.D."),
    (r"\b(?:M\.?S\.?|M\.?Sc\.?|Master of Science|Master's Degree|M\.?Tech|MCA|MBA)\b", "Master's Degree"),
    (r"\b(?:B\.?S\.?|B\.?Sc\.?|Bachelor of Science|Bachelor's Degree|B\.?Tech|B\.?E\.?|BCA|BBA)\b", "Bachelor's Degree"),
    (r"\b(?:Associate Degree|A\.?S\.?|A\.?A\.?)\b", "Associate Degree"),
]

class ResumeParser:
    """Production-grade resume parser supporting PDF, DOCX, and TXT."""

    def extract_text_from_file(self, file_path: str) -> str:
        """Extracts and normalizes raw text from PDF, DOCX, or TXT."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if not path.exists():
            raise FileNotFoundError(f"Resume file not found at {file_path}")

        raw_text = ""
        try:
            if ext == ".pdf":
                raw_text = self._extract_pdf(path)
            elif ext in [".docx", ".doc"]:
                raw_text = self._extract_docx(path)
            elif ext == ".txt":
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

        return self.clean_text(raw_text)

    def _extract_pdf(self, path: Path) -> str:
        text_parts = []
        with fitz.open(str(path)) as doc:
            for page in doc:
                text = page.get_text("text")
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)

    def _extract_docx(self, path: Path) -> str:
        doc = Document(str(path))
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)
        return "\n".join(text_parts)

    def clean_text(self, text: str) -> str:
        """Cleans and standardizes extracted text."""
        if not text:
            return ""
        # Replace non-breaking spaces and unusual whitespace
        text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
        # Remove repeated excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove consecutive trailing spaces
        text = "\n".join(line.strip() for line in text.split("\n"))
        return text.strip()

    def segment_sections(self, text: str) -> Dict[str, str]:
        """Segments resume into standard sections using header heuristics."""
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {
            "header": [],
            "summary": [],
            "experience": [],
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "other": [],
        }

        current_section = "header"
        all_header_names = {}
        for sec, keywords in SECTION_HEADERS.items():
            for kw in keywords:
                all_header_names[kw] = sec

        for line in lines:
            trimmed = line.strip().lower()
            # Remove punctuation like colons, dashes
            cleaned_header = re.sub(r"[:\-_#*]", "", trimmed).strip()

            detected_section = None
            if len(cleaned_header) < 40:
                if cleaned_header in all_header_names:
                    detected_section = all_header_names[cleaned_header]
                else:
                    for kw, sec in all_header_names.items():
                        if cleaned_header == kw or (len(kw) > 4 and cleaned_header.startswith(kw)):
                            detected_section = sec
                            break

            if detected_section:
                current_section = detected_section
            else:
                sections[current_section].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    def extract_candidate_name(self, text: str, header_text: str) -> str:
        """Extracts candidate name from the top header lines."""
        lines = [line.strip() for line in (header_text + "\n" + text).split("\n") if line.strip()]
        
        # Stop words that cannot be candidate names
        ignore_words = {
            "resume", "curriculum vitae", "cv", "page", "contact", "email", "phone",
            "profile", "summary", "experience", "education", "skills", "projects",
            "developer", "engineer", "software", "analyst", "senior", "junior", "lead"
        }

        for line in lines[:6]:
            clean = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            words = clean.split()
            if 2 <= len(words) <= 4:
                lower_line = clean.lower()
                if not any(ign in lower_line for ign in ignore_words):
                    # Check that words look like names (capitalized or title case)
                    return clean.title()

        return "Candidate"

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extracts email, phone, LinkedIn, GitHub URLs."""
        email_match = EMAIL_REGEX.search(text)
        email = email_match.group(0).lower() if email_match else None

        phone_match = PHONE_REGEX.search(text)
        phone = phone_match.group(0).strip() if phone_match else None
        # Clean phone if too short or long
        if phone:
            digits = re.sub(r"\D", "", phone)
            if len(digits) < 7 or len(digits) > 15:
                phone = None

        linkedin_match = LINKEDIN_REGEX.search(text)
        linkedin = (
            f"https://linkedin.com/in/{linkedin_match.group(1)}"
            if linkedin_match
            else None
        )

        github_match = GITHUB_REGEX.search(text)
        github = (
            f"https://github.com/{github_match.group(1)}"
            if github_match
            else None
        )

        return {
            "email": email,
            "phone": phone,
            "linkedin_url": linkedin,
            "github_url": github,
        }

    def extract_education(self, text: str, education_section: str) -> List[EducationItem]:
        """Identifies degrees, institutions, and years."""
        target_text = education_section if education_section else text
        items: List[EducationItem] = []
        lines = target_text.split("\n")

        year_regex = re.compile(r"\b(19\d{2}|20\d{2})\b")

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            for pattern, degree_label in DEGREE_PATTERNS:
                if re.search(pattern, line_str, re.IGNORECASE):
                    year_match = year_regex.search(line_str)
                    year = year_match.group(0) if year_match else None

                    # Heuristic for institution name
                    institution = None
                    parts = re.split(r"[,|\-–]", line_str)
                    for p in parts:
                        clean_p = p.strip()
                        if any(term in clean_p.lower() for term in ["university", "college", "institute", "school", "academy", "polytechnic"]):
                            institution = clean_p
                            break

                    items.append(
                        EducationItem(
                            degree=degree_label,
                            institution=institution or "Recognized Institution",
                            graduation_year=year,
                        )
                    )
                    break

        if not items and ("bachelor" in target_text.lower() or "b.s." in target_text.lower() or "b.tech" in target_text.lower()):
            items.append(EducationItem(degree="Bachelor's Degree", institution="University"))

        return items

    def extract_experience(
        self, text: str, experience_section: str
    ) -> Tuple[List[WorkExperienceItem], float, bool]:
        """Extracts work experience items, total estimated years, and uncertainty flag."""
        target_text = experience_section if experience_section else text
        items: List[WorkExperienceItem] = []
        
        # Regex for date ranges: e.g. "2019 - 2022", "Jan 2020 - Present", "06/2018 - 08/2021"
        date_range_regex = re.compile(
            r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+)?\b(20\d{2}|19\d{2})\b\s*(?:-|–|to)\s*((?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+)?\b(?:20\d{2}|19\d{2})\b|present|current)",
            re.IGNORECASE
        )

        lines = target_text.split("\n")
        total_years = 0.0
        ranges_found = 0
        current_year = 2026

        for i, line in enumerate(lines):
            match = date_range_regex.search(line)
            if match:
                ranges_found += 1
                start_year = int(match.group(2))
                end_str = match.group(3).strip().lower()

                if "present" in end_str or "current" in end_str:
                    end_year = current_year
                else:
                    year_match = re.search(r"\b(20\d{2}|19\d{2})\b", end_str)
                    end_year = int(year_match.group(0)) if year_match else start_year

                duration_years = max(0.5, float(end_year - start_year))
                total_years += duration_years

                # Look for title in current or previous line
                title_line = lines[i - 1].strip() if i > 0 and len(lines[i - 1].strip()) < 80 else line.strip()
                items.append(
                    WorkExperienceItem(
                        title=title_line[:70],
                        duration=match.group(0),
                        years=duration_years,
                        description=line.strip(),
                    )
                )

        # Check explicit mentions like "5+ years of experience"
        explicit_match = re.search(r"\b(\d{1,2}(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience\b", text, re.IGNORECASE)
        if explicit_match:
            explicit_years = float(explicit_match.group(1))
            total_years = max(total_years, explicit_years)

        # If no dates found, flag as uncertain
        uncertain = False
        if ranges_found == 0 and not explicit_match:
            uncertain = True
            # Check if there is an experience section with words
            if len(experience_section.strip()) > 100:
                total_years = 1.0  # conservative baseline
            else:
                total_years = 0.0

        return items, round(total_years, 1), uncertain

    def extract_projects(self, projects_section: str) -> List[ProjectItem]:
        """Extracts project headings and tech stack mentions."""
        if not projects_section:
            return []
        items: List[ProjectItem] = []
        blocks = re.split(r"\n(?=[A-Z0-9][\w\s]{2,40}(?::| - | \||\n))", projects_section)
        
        for block in blocks:
            b_lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not b_lines:
                continue
            title = b_lines[0][:60]
            desc = " ".join(b_lines[1:])[:300] if len(b_lines) > 1 else ""
            
            # Find skills mentioned in this project
            found_skills = [
                s.canonical_name for s in skill_extractor.extract_skills(block)
            ]
            items.append(
                ProjectItem(
                    title=title,
                    description=desc,
                    technologies=list(set(found_skills)),
                )
            )
        return items[:6]

    def extract_certifications(self, cert_section: str, full_text: str) -> List[str]:
        """Extracts recognizable certifications."""
        target = cert_section if cert_section else full_text
        cert_keywords = [
            "AWS Certified", "Solutions Architect", "Developer Associate",
            "CKA", "Certified Kubernetes", "Azure Fundamentals", "Azure Solutions Architect",
            "GCP Professional", "PMP", "Scrum Master", "CISSP", "CompTIA Security+",
            "TensorFlow Developer", "Google Cloud Certified"
        ]
        found = []
        for kw in cert_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", target, re.IGNORECASE):
                found.append(kw)
        return found

    def parse(self, file_path: str) -> Tuple[str, ParsedResumeData]:
        """Full pipeline: reads document, extracts text, identifies entities, returns parsed data."""
        raw_text = self.extract_text_from_file(file_path)
        sections = self.segment_sections(raw_text)
        
        contacts = self.extract_contact_info(raw_text)
        candidate_name = self.extract_candidate_name(raw_text, sections.get("header", ""))
        
        # Skill extraction from full resume text
        skills = skill_extractor.extract_skills(raw_text)

        # Education
        education = self.extract_education(raw_text, sections.get("education", ""))

        # Work Experience
        work_exp, exp_years, uncertain = self.extract_experience(raw_text, sections.get("experience", ""))

        # Projects
        projects = self.extract_projects(sections.get("projects", ""))

        # Certifications
        certs = self.extract_certifications(sections.get("certifications", ""), raw_text)

        summary_text = sections.get("summary") or sections.get("header")
        if summary_text and len(summary_text) > 400:
            summary_text = summary_text[:397] + "..."

        current_role = work_exp[0].title if work_exp else None

        parsed_data = ParsedResumeData(
            name=candidate_name,
            email=contacts.get("email"),
            phone=contacts.get("phone"),
            linkedin_url=contacts.get("linkedin_url"),
            github_url=contacts.get("github_url"),
            summary=summary_text,
            education=education,
            work_experience=work_exp,
            skills=skills,
            projects=projects,
            certifications=certs,
            estimated_experience_years=exp_years,
            experience_uncertain=uncertain,
        )

        return raw_text, parsed_data

# Singleton instance
resume_parser = ResumeParser()
