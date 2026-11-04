import re
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.resume import SkillItem

# Comprehensive skill taxonomy categorized into standard engineering domains
SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": {
        "Python": ["python", "python3", "py"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "Java": ["java", "j2ee", "core java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp", ".net c#"],
        "Go": ["golang", "go language"],  # handled specially to avoid common English 'go'
        "Rust": ["rust", "rust-lang"],
        "Ruby": ["ruby", "ruby on rails", "rails"],
        "PHP": ["php", "php7", "php8"],
        "Swift": ["swift", "swiftui"],
        "Kotlin": ["kotlin"],
        "Scala": ["scala"],
        "R": ["r programming", "r-project"],
        "SQL": ["sql", "structured query language"],
        "Bash": ["bash", "shell scripting", "sh", "zsh"],
        "HTML/CSS": ["html", "html5", "css", "css3"],
    },
    "Web Development": {
        "React": ["react", "react.js", "reactjs"],
        "Node.js": ["node", "node.js", "nodejs"],
        "FastAPI": ["fastapi", "fast-api"],
        "Django": ["django", "django rest framework", "drf"],
        "Flask": ["flask"],
        "Express": ["express", "express.js", "expressjs"],
        "Next.js": ["next.js", "nextjs"],
        "Vue": ["vue", "vue.js", "vuejs"],
        "Angular": ["angular", "angularjs", "angular2+"],
        "Spring Boot": ["spring boot", "springboot", "spring framework"],
        "GraphQL": ["graphql"],
        "REST APIs": ["rest", "rest api", "restful", "restful apis", "rest apis", "web apis"],
        "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind-css"],
        "Bootstrap": ["bootstrap"],
    },
    "Databases": {
        "PostgreSQL": ["postgresql", "postgres", "psql"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Cassandra": ["cassandra", "apache cassandra"],
        "Elasticsearch": ["elasticsearch", "elastic search", "elk"],
        "DynamoDB": ["dynamodb", "aws dynamodb"],
        "Supabase": ["supabase"],
        "Neo4j": ["neo4j"],
        "Firebase": ["firebase", "firestore"],
    },
    "Cloud & DevOps": {
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "ecs", "eks"],
        "Azure": ["azure", "microsoft azure"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Docker": ["docker", "containerization", "containers"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Terraform": ["terraform", "iac"],
        "CI/CD": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"],
        "GitHub Actions": ["github actions", "gh actions"],
        "Jenkins": ["jenkins"],
        "Git": ["git", "github", "gitlab", "version control"],
        "Linux": ["linux", "ubuntu", "debian", "centos", "redhat"],
        "Nginx": ["nginx"],
        "Ansible": ["ansible"],
    },
    "AI / ML & Data Science": {
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "dl"],
        "Natural Language Processing": ["nlp", "natural language processing"],
        "Computer Vision": ["computer vision", "cv", "opencv"],
        "PyTorch": ["pytorch", "torch"],
        "TensorFlow": ["tensorflow", "tf"],
        "Scikit-Learn": ["scikit-learn", "sklearn", "scikit learn"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Sentence Transformers": ["sentence transformers", "sentence-transformers", "sbert"],
        "Transformers": ["transformers", "huggingface", "hugging face"],
        "spaCy": ["spacy"],
        "LLMs": ["llm", "llms", "large language models", "generative ai", "genai", "gpt"],
        "LangChain": ["langchain"],
        "LlamaIndex": ["llamaindex"],
        "Data Visualization": ["data visualization", "matplotlib", "seaborn", "tableau", "powerbi"],
    },
    "Software Engineering Tools": {
        "Microservices": ["microservices", "microservice architecture"],
        "Agile": ["agile", "scrum", "kanban", "sprints"],
        "Jira": ["jira", "confluence"],
        "Unit Testing": ["unit testing", "pytest", "jest", "junit", "tdd", "test driven development"],
        "Design Patterns": ["design patterns", "oop", "object oriented programming"],
        "System Design": ["system design", "distributed systems", "high availability"],
    },
    "Cybersecurity": {
        "Cybersecurity": ["cybersecurity", "cyber security", "infosec", "information security"],
        "Penetration Testing": ["penetration testing", "pen testing", "ethical hacking"],
        "OWASP": ["owasp", "owasp top 10"],
        "Cryptography": ["cryptography", "encryption", "tls", "ssl"],
        "Network Security": ["network security", "firewall", "ids/ips"],
        "IAM": ["iam", "identity and access management", "oauth", "jwt"],
    }
}

class SkillExtractor:
    """Robust, boundary-safe NLP skill extraction engine."""

    def __init__(self):
        self.alias_to_canonical: Dict[str, Tuple[str, str]] = {}
        self.canonical_to_category: Dict[str, str] = {}
        self.compiled_patterns: List[Tuple[re.Pattern, str, str]] = []

        self._build_indexes()

    def _build_indexes(self):
        for category, skills in SKILL_TAXONOMY.items():
            for canonical, aliases in skills.items():
                self.canonical_to_category[canonical] = category
                all_variants = set(aliases + [canonical.lower()])
                for alias in all_variants:
                    clean_alias = alias.lower().strip()
                    self.alias_to_canonical[clean_alias] = (canonical, category)

                    # Build safe boundary regex pattern
                    # Handle special characters like ++, #, ., /
                    escaped = re.escape(clean_alias)
                    # Word boundary adjustment for symbols
                    if clean_alias in ["c++", "cpp"]:
                        pattern = re.compile(r"(?i)(?:\bcpp\b|\bc\+\+(?=[^a-z0-9]|$))")
                    elif clean_alias in ["c#", "csharp"]:
                        pattern = re.compile(r"(?i)(?:\bcsharp\b|\bc\#(?=[^a-z0-9]|$))")
                    elif clean_alias == "r":
                        # Strict: only "R programming" or "R language"
                        pattern = re.compile(r"(?i)\br\s+(?:programming|language|script)\b")
                    elif clean_alias == "go":
                        # Strict: "Go language", "Golang", or Go in uppercase with programming context
                        pattern = re.compile(r"(?i)\bgolang\b|\bGo\s+(?:language|developer|programming|backend)\b")
                    elif clean_alias == "c":
                        pattern = re.compile(r"(?i)\bc\s+(?:programming|language)\b")
                    elif clean_alias == "ml":
                        pattern = re.compile(r"(?i)\bml\b(?:\s+(?:models|algorithms|engineer|pipeline))?|\bmachine\s+learning\b")
                    elif clean_alias == "dl":
                        pattern = re.compile(r"(?i)\bdl\b(?:\s+(?:models|algorithms|engineer))?|\bdeep\s+learning\b")
                    else:
                        pattern = re.compile(r"(?i)(?<![a-zA-Z0-9])" + escaped + r"(?![a-zA-Z0-9])")
                    
                    self.compiled_patterns.append((pattern, canonical, category))

    def extract_skills(self, text: str) -> List[SkillItem]:
        """Extracts normalized skills along with context evidence sentences."""
        if not text:
            return []

        # Split into sentences / bullet points for context evidence
        raw_sentences = re.split(r"(?<=[.!?\n])\s+", text)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]

        found_skills: Dict[str, Dict[str, Any]] = {}

        for pattern, canonical, category in self.compiled_patterns:
            if canonical in found_skills:
                # Already matched canonical skill, maybe look for stronger evidence
                continue

            match = pattern.search(text)
            if match:
                matched_text = match.group(0)
                # Find the sentence containing this match for evidence
                evidence = ""
                for s in sentences:
                    if pattern.search(s):
                        # Shorten if too long
                        evidence = s.strip()
                        if len(evidence) > 200:
                            evidence = evidence[:197] + "..."
                        break

                if not evidence:
                    start_idx = max(0, match.start() - 40)
                    end_idx = min(len(text), match.end() + 40)
                    evidence = f"...{text[start_idx:end_idx].strip()}..."

                found_skills[canonical] = {
                    "name": matched_text,
                    "canonical_name": canonical,
                    "category": category,
                    "evidence_snippet": evidence,
                    "confidence": 1.0,
                }

        # Convert to SkillItem models
        results = [
            SkillItem(
                name=info["name"],
                canonical_name=info["canonical_name"],
                category=info["category"],
                evidence_snippet=info["evidence_snippet"],
                confidence=info["confidence"],
            )
            for info in sorted(found_skills.values(), key=lambda x: (x["category"], x["canonical_name"]))
        ]
        return results

    def normalize_skill(self, skill_name: str) -> Optional[Tuple[str, str]]:
        """Normalize a single skill string to (canonical_name, category) if recognized."""
        cleaned = skill_name.lower().strip()
        if cleaned in self.alias_to_canonical:
            return self.alias_to_canonical[cleaned]
        # Partial match fallback
        for pattern, canonical, category in self.compiled_patterns:
            if pattern.search(skill_name):
                return (canonical, category)
        return None

# Singleton instance
skill_extractor = SkillExtractor()
