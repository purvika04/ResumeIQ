import pytest
from pathlib import Path
from app.services.resume_parser import resume_parser

def test_clean_text():
    raw = "  Hello \u00a0 World! \r\n\r\n\r\n This is a resume.  "
    cleaned = resume_parser.clean_text(raw)
    assert "\u00a0" not in cleaned
    assert "\r" not in cleaned
    assert "Hello   World!" in cleaned or "Hello World!" in cleaned

def test_extract_contact_info():
    text = (
        "John Doe\n"
        "Email: john.doe@example.com\n"
        "Phone: (415) 555-1234\n"
        "LinkedIn: https://linkedin.com/in/johndoe-dev\n"
        "GitHub: https://github.com/johndoe-code\n"
    )
    contacts = resume_parser.extract_contact_info(text)
    assert contacts["email"] == "john.doe@example.com"
    assert contacts["phone"] is not None
    assert "linkedin.com/in/johndoe-dev" in contacts["linkedin_url"]
    assert "github.com/johndoe-code" in contacts["github_url"]

def test_extract_candidate_name():
    text = (
        "Sarah Connor\n"
        "Email: sarah.connor@sky.net\n"
        "Summary: Senior Developer with 10 years experience."
    )
    name = resume_parser.extract_candidate_name(text, "Sarah Connor\nEmail: sarah.connor@sky.net")
    assert name == "Sarah Connor"

def test_parse_sample_file():
    # Use one of the generated sample files
    sample_file = Path(__file__).resolve().parent.parent.parent / "sample_data" / "resumes" / "priya_sharma.txt"
    if sample_file.exists():
        raw_text, parsed = resume_parser.parse(str(sample_file))
        assert parsed.name == "Priya Sharma"
        assert parsed.email == "priya.sharma.dev@gmail.com"
        assert len(parsed.skills) > 0
        assert parsed.estimated_experience_years >= 2.0
