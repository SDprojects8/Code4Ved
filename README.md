# Code4Ved - Vedic Texts Analysis Platform

> **Bridging Ancient Wisdom with Modern Technology**  
> A comprehensive digital platform for accessing, analyzing, and exploring Vedic literature through web scraping, database management, NLP analysis, and knowledge graph visualization.

![Project Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

---

## 📖 Table of Contents
- [Overview](#overview)
- [Project Genesis](#project-genesis)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Technology Stack](#technology-stack)
- [Project Objectives](#project-objectives)
- [Text Sources](#text-sources)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Risks & Mitigations](#risks--mitigations)
- [References](#references)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

**Code4Ved** is a self-directed learning project that combines programming expertise with the study of ancient Indian texts (Vedas, Puranas, Upanishads, Samhitas, Epic Poems). The platform aims to:

- **Centralize Access**: Aggregate texts from 15+ Sanskrit repositories into a unified database
- **Enable Analysis**: Apply NLP techniques to extract philosophical concepts and themes
- **Visualize Relationships**: Create knowledge graphs connecting ancient wisdom with modern science
- **Build Learning Paths**: Generate interactive roadmaps for systematic study
- **Develop Skills**: Gain hands-on experience with Python, SQL, web scraping, NLP, and graph databases

### Vision
Make 1000+ years of ancient wisdom accessible through modern computational tools while creating reusable open-source infrastructure for the Sanskrit studies community.

---

## 🌱 Project Genesis

This project was initiated in April 2025 following extensive research consultations with multiple AI assistants (Gemini, Copilot, Claude, Perplexity, DeepSeek, Grok, Krutrim, and others) exploring ways to combine programming skills with the study of Vedic literature.

### Research Timeline
- **2025-04-18**: Initial question posed: "How can I leverage programming skills while studying Vedas, Puranas, and Upanishads?"
- **2025-04-19**: Identified 5 core project ideas and compiled initial list of text sources
- **2025-04-26**: Refined technical approach across multiple AI consultations
- **2025-04-27**: Consolidated resources and implementation strategies
- **2025-05-19**: Generated Mermaid classification charts using Python
- **2025-10-04**: Formalized project charter and documentation structure

---

## ✨ Key Features

### 1. **Multi-Source Web Scraping**
- Automated text extraction from 15+ Sanskrit repositories
- Support for PDF, HTML, and plain text formats
- Ethical scraping with rate limiting and robots.txt compliance
- Comprehensive scraping logs for audit trails

### 2. **Multi-Dimensional Classification**
Texts classified across 5 dimensions:
- **Language**: English, Hindi, Sanskrit, Mixed
- **Format**: PDF, HTML, Plain Text
- **Category**: Vedas, Puranas, Upanishads, Samhitas, Epic Poems
- **Philosophical Concepts**: Atman, Brahman, Karma, Dharma, Moksha, Maya, Yoga, Bhakti
- **Themes**: Spirituality, Philosophy, War, Medicine, Mathematics, Art, Duty, Ritual, Cosmology

### 3. **Multi-Database Architecture**
- **PostgreSQL**: Structured metadata and relationships
- **MongoDB**: Unstructured annotations and commentary
- **Neo4j**: Graph database for concept relationships
- **SQLite3**: Lightweight development and prototyping

### 4. **NLP Analysis Pipeline**
- Keyword extraction using NLTK and spaCy
- Topic modeling with LDA
- Concept co-occurrence analysis
- Automated concept tagging with confidence scores
- Manual validation workflow

### 5. **Knowledge Graph**
- Visual representation of relationships between:
  - Philosophical concepts (Atman, Brahman, Karma)
  - Scientific topics (Quantum Mechanics, Cosmology, Mathematics)
  - Texts and their interconnections
- Graph traversal queries for exploration
- >500 nodes and >1000 relationships

### 6. **Learning Roadmap Visualization**
- Interactive flowcharts following GitHub roadmap patterns
- Recommended reading order
- Prerequisite mapping
- Exportable as SVG/PNG

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  Web Scrapers       │  ← Python/GoLang/Rust
│  (BeautifulSoup,    │
│   Scrapy, reqwest)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Processing    │  ← PyPDF2, text cleaning
│  & Extraction       │     pdfminer.six
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│         Database Layer              │
│  ┌─────────┬─────────┬───────────┐ │
│  │PostgreSQL│ MongoDB │  Neo4j    │ │
│  │(metadata)│(comments)│ (graph)  │ │
│  └─────────┴─────────┴───────────┘ │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  NLP Pipeline       │  ← NLTK, spaCy
│  (Analysis)         │     scikit-learn
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Visualization      │  ← Mermaid, NetworkX
│  & Query Interface  │     Matplotlib, D3.js
└─────────────────────┘
```

---

## 📊 Data Model

### Entity Relationship Overview

```
Texts (1) ──── (M) Text_Concepts ──── (M) Concepts
  │                                         │
  │                                         │
  └──── (M) Text_Themes ──── (M) Themes    │
                                            │
                                   (Graph) Concept_Relationships
                                            │
                                   (Graph) Scientific_Topics
```

### PostgreSQL Schema Highlights

**Core Tables**:
- `texts`: Title, language, format, category, source URL, content, content_hash
- `philosophical_concepts`: Concept name, Sanskrit term, description, category
- `themes`: Theme name, description
- `text_concepts`: Junction table with occurrence count, context, confidence
- `text_themes`: Junction table with relevance scores
- `scraping_log`: Audit trail of all scraping activities

**Key Features**:
- Full-text search indexes on content and titles
- Content hash for duplicate detection
- Foreign key relationships with CASCADE delete
- CHECK constraints on enumerations
- Confidence scores (0.0-1.0) for automated extractions

### MongoDB Schema

**Collection: annotations**
```json
{
  "text_id": 123,
  "annotations": [{
    "annotation_id": "uuid",
    "type": "commentary|note|translation|question",
    "content": "Annotation text",
    "tags": ["atman", "metaphysics"],
    "verse_reference": "Chapter 2, Verse 15"
  }]
}
```

### Neo4j Graph Schema

**Node Types**:
- `PhilosophicalConcept`: {concept_id, name, sanskrit_term, category}
- `ScientificTopic`: {topic_id, name, field}
- `Text`: {text_id, title, category}

**Relationship Types**:
- `RELATES_TO`: Concept → Concept (with strength, cooccurrence_count)
- `CONNECTS_TO`: Concept → Scientific Topic (with connection_strength, evidence)
- `MENTIONED_IN`: Concept → Text (with occurrence_count, prominence)

---

## 💻 Technology Stack

| Component | Technologies | Purpose |
|-----------|-------------|---------|
| **Web Scraping** | Python (requests, BeautifulSoup, Scrapy), Bash (wget, curl), Rust (reqwest, scraper), Go (colly) | Text extraction from websites |
| **PDF Processing** | PyPDF2, pdfminer.six, pdfplumber | Extract text from PDF files |
| **Databases** | PostgreSQL (structured data), MongoDB (unstructured data), Neo4j (graph), SQLite3 (development) | Multi-database architecture |
| **NLP** | NLTK, spaCy, scikit-learn (LDA) | Text analysis, concept extraction, topic modeling |
| **Visualization** | Mermaid.js, Graphviz, NetworkX, Matplotlib, D3.js | Flowcharts, graphs, roadmaps |
| **Languages** | Python (primary), GoLang (performance), Rust (safety), C++ (optimization) | Progressive skill development |
| **Version Control** | Git, GitHub | Code management and collaboration |
| **Automation** | Ansible, Bash scripts | Deployment and task automation |

---

## 🎯 Project Objectives

### Primary Objectives
1. Create comprehensive database of 100+ texts from 10+ major repositories
2. Build automated web scraping tools for text extraction
3. Develop NLP pipeline for Sanskrit text analysis
4. Implement knowledge graph connecting philosophy with modern science
5. Design interactive learning path visualization

### Success Criteria
- ✅ Extract and classify 100+ texts from at least 10 websites
- ✅ Database contains multi-dimensional classifications
- ✅ NLP tools achieve >80% accuracy on manual validation
- ✅ Knowledge graph contains >500 nodes and >1000 relationships
- ✅ Interactive learning roadmap created and accessible
- ✅ Well-documented codebase for future enhancements

---

## 📚 Text Sources

### Primary Repositories (High Reliability)

| Source | URL | Type | Notes |
|--------|-----|------|-------|
| Vedic Heritage Portal | https://vedicheritage.gov.in/ | Official govt repository | Comprehensive, high reliability |
| GRETIL | http://gretil.sub.uni-goettingen.de/ | Academic | University of Göttingen, peer-reviewed |
| Ambuda.org | https://ambuda.org/ | Open Source | Active development, tools available |
| GITA Supersite | https://www.gitasupersite.iitk.ac.in/ | Academic | IIT Kanpur, comprehensive |
| Sanskrit Library | https://sanskritlibrary.org/ | Academic | High academic standards |
| TITUS | https://titus.fkidg1.uni-frankfurt.de/ | Academic | University Frankfurt linguistic database |
| IGNCA | https://ignca.gov.in/divisionss/asi-books/ | Government | Indira Gandhi National Centre for the Arts |
| Sanskrit DCS | http://www.sanskrit-linguistics.org/dcs/ | Academic | Digital Corpus with linguistic tools |

### Secondary Repositories (Medium Reliability)

| Source | URL | Type | Notes |
|--------|-----|------|-------|
| Sanskrit Documents | https://sanskritdocuments.org/ | Community | Large collection, varying quality |
| Sacred Texts | https://www.sacred-texts.com/hin/ | Archive | Historical archive, public domain |
| Ved Puran | https://vedpuran.net/ | Community | PDF downloads available |
| Sanskrit Books | https://www.sanskritebooks.org/ | Digital Library | Wide collection |
| Veducation World | https://www.veducation.world/library | Educational | Learning-focused content |
| Adhyeta.org | https://www.adhyeta.org.in/ | Learning Platform | Educational resources |

### GitHub Resources
- **Ambuda Repository**: https://github.com/ambuda-org - Sanskrit tools reference
- **Awesome Roadmaps**: https://github.com/liuchong/awesome-roadmaps - Learning path patterns

---

## 🚀 Installation

### Prerequisites
```bash
# Python 3.8+
python --version

# PostgreSQL
psql --version

# MongoDB
mongod --version

# Neo4j (optional, for graph database)
neo4j version
```

### Setup

```bash
# Clone the repository
git clone https://github.com/RustyNails8/Code4Ved.git
cd Code4Ved

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up databases
# PostgreSQL
createdb code4ved
psql code4ved < schema/postgres_schema.sql

# MongoDB (ensure mongod is running)
mongosh
use vedic_texts
db.createCollection("annotations")

# Neo4j (optional)
# Start Neo4j and create database via web interface
```

### Configuration
```bash
# Copy example config
cp config.example.yml config.yml

# Edit config.yml with your database credentials
nano config.yml
```

---

## 📖 Usage

### Basic Web Scraping
```bash
# Scrape a single website
python src/code4ved/scrapers/scrape_text.py --url https://vedicheritage.gov.in/

# Batch scraping from source list
python src/code4ved/scrapers/batch_scrape.py --sources config/sources.yml
```

### Text Classification
```bash
# Classify extracted texts
python src/code4ved/classify/classify_texts.py --input data/raw/ --output data/processed/

# Manually review classifications
python src/code4ved/classify/review_tool.py
```

### NLP Analysis
```bash
# Extract keywords
python src/code4ved/nlp/extract_keywords.py --text-id 123

# Topic modeling
python src/code4ved/nlp/topic_model.py --corpus data/processed/

# Concept extraction
python src/code4ved/nlp/extract_concepts.py --text-id 123
```

### Database Operations
```bash
# Insert text into database
python src/code4ved/db/insert_text.py --file data/processed/rigveda.txt

# Query database
python src/code4ved/db/query.py --category Vedas --language Sanskrit

# Export to JSON
python src/code4ved/db/export.py --format json --output exports/
```

### Visualization
```bash
# Generate learning roadmap
python src/code4ved/viz/generate_roadmap.py --output assets/roadmap.svg

# Create concept graph
python src/code4ved/viz/concept_graph.py --output assets/concept_graph.html
```

---

## 📁 Project Structure

```
Code4Ved/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── pyproject.toml                    # Project configuration
├── Makefile                          # Build automation
│
├── src/                              # Source code
│   └── code4ved/
│       ├── __init__.py
│       ├── scrapers/                 # Web scraping modules
│       ├── db/                       # Database operations
│       ├── nlp/                      # NLP pipeline
│       ├── viz/                      # Visualization tools
│       └── utils/                    # Utility functions
│
├── data/                             # Data directory
│   ├── external/                     # Research notes and external data
│   ├── raw/                          # Raw scraped data
│   └── processed/                    # Processed and classified data
│
├── docs/                             # Documentation
│   ├── agents/                       # Agent-based workflow docs
│   ├── guides/                       # User guides
│   └── source/                       # Source documentation
│
├── project-management/               # Project management artifacts
│   ├── 00_inbox/                     # Ideas and triage
│   ├── 01_project-charter/          # Charter, scope, stakeholders
│   ├── 02_research/                  # Research notes and references
│   ├── 03_specifications/           # FSD, TSD, NFR, data model
│   ├── 04_planning/                  # Roadmap, milestones, WBS
│   ├── 05_design/                    # Architecture, design docs
│   ├── 06_implementation/           # Development plans
│   ├── 07_testing/                   # Test strategy and cases
│   ├── 08_release/                   # Release plans
│   ├── 09_operations/               # SLA, monitoring, runbooks
│   ├── 10_documentation/            # User/admin guides
│   ├── 11_retrospective/            # Lessons learned
│   └── 12_risks/                     # Risk register, decisions
│
├── tests/                            # Test suite
│   ├── 01_FUT_functional_unit_tests/
│   ├── 02_SIT_system_integration_tests/
│   └── 03_UAT_E2E_end-to-end_tests/
│
├── scripts/                          # Utility scripts
├── examples/                         # Example usage
├── assets/                           # Images, diagrams, charts
├── logs/                             # Application logs
└── prompts/                          # AI agent prompts
    ├── Manager_Agent/
    ├── Implementation_Agent/
    ├── Setup_Agent/
    ├── ad-hoc/
    ├── guides/
    └── schemas/
```

---

## 🗺️ Roadmap

### Phase 1: Data Collection (Q1 2025)
- [x] Research AI consultations (2025-04-18 to 2025-04-27)
- [x] Identify text sources (15+ websites)
- [ ] Build web scraping module (Python)
- [ ] Extract texts from 10 primary sources
- [ ] Set up PostgreSQL and MongoDB databases

### Phase 2: Classification & Database (Q2 2025)
- [ ] Implement text classification system
- [ ] Populate databases with extracted texts
- [ ] Manual validation of 100 sample texts
- [ ] Build query interface
- [ ] Create database backup procedures

### Phase 3: NLP Analysis (Q3 2025)
- [ ] Develop keyword extraction pipeline
- [ ] Implement topic modeling (LDA)
- [ ] Build concept extraction tools
- [ ] Achieve >80% accuracy on validation set
- [ ] Create annotation workflow

### Phase 4: Knowledge Graph (Q3-Q4 2025)
- [ ] Set up Neo4j graph database
- [ ] Define node and relationship types
- [ ] Populate graph with philosophical concepts
- [ ] Create connections to scientific topics
- [ ] Build graph visualization tools

### Phase 5: Visualization & Release (Q4 2025)
- [ ] Generate learning roadmap (Mermaid)
- [ ] Create concept relationship graphs
- [ ] Build web interface (optional)
- [ ] Complete documentation
- [ ] Publish to GitHub

### Future Enhancements
- [ ] Explore GoLang/Rust implementations for performance
- [ ] Add Sanskrit-specific NLP tools
- [ ] Implement collaborative annotation features
- [ ] Develop mobile application
- [ ] Create REST API for external access
- [ ] Build recommendation system for reading paths

---

## 🤝 Contributing

Contributions are welcome! This is an open-source project aimed at making Vedic literature more accessible.

### How to Contribute
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/YourFeature`
3. **Commit changes**: `git commit -m 'Add YourFeature'`
4. **Push to branch**: `git push origin feature/YourFeature`
5. **Open a Pull Request**

### Contribution Areas
- **Text Sources**: Identify additional reliable Sanskrit repositories
- **NLP Improvements**: Enhance Sanskrit text processing
- **Classification**: Help tag and validate text classifications
- **Visualization**: Improve roadmap and graph visualizations
- **Documentation**: Improve guides and tutorials
- **Testing**: Add unit tests and integration tests
- **Bug Fixes**: Report and fix bugs

### Code Standards
- Follow PEP 8 for Python code
- Write docstrings for all functions
- Add unit tests for new features
- Update documentation as needed

---

## ⚠️ Risks & Mitigations

### High Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| **Copyright/Licensing Violations** | Medium | High | - Use only verified public domain sources<br>- Check website ToS before scraping<br>- Maintain clear attribution<br>- Prioritize government/academic sources |
| **Sanskrit NLP Accuracy Limitations** | High | Medium | - Start with English translations<br>- Set confidence thresholds<br>- Implement manual validation<br>- Accept higher curation burden |

### Medium Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| **Website Structure Changes** | Medium | Medium | - Build flexible scrapers<br>- Regular testing<br>- Maintain test suite<br>- Have backup sources |
| **Scope Creep** | High | Medium | - Strict feature prioritization<br>- MVP mindset<br>- Track ideas in backlog<br>- Regular scope reviews |
| **Time Commitment Conflicts** | Medium | Medium | - Realistic scheduling<br>- Modular development<br>- Accept longer timeline<br>- Focus on valuable components |
| **Data Quality Issues** | Medium | Medium | - Prioritize high-quality sources<br>- Data validation rules<br>- Standardized preprocessing<br>- Manual quality checks |
| **Data/Code Loss** | Low | High | - Git version control<br>- GitHub remote repository<br>- Regular database backups<br>- Test restore procedures |

### Low Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| **Technical Complexity Exceeds Skills** | Low | Medium | - Start with known technologies<br>- Progressive learning<br>- Extensive tutorials<br>- Simplify if needed |
| **Database Performance Issues** | Low | Low | - Proper indexing<br>- Query optimization<br>- Monitor performance<br>- Implement caching |

---

## 📚 References

### Primary Research Sources

**AI Consultations** (2025-04-18 to 2025-04-27):
- Gemini (Google AI): Project approach, technical architecture
- Copilot (Microsoft/GitHub): Implementation strategies, NLP pipelines
- Claude (Anthropic): Systematic approach, learning applications
- Perplexity AI: Academic connections, research papers
- DeepSeek AI: Code examples, implementations
- Grok (xAI): Comprehensive methodology
- Meta AI: Technology options, knowledge graphs
- Krutrim AI: Indian context, Sanskrit NLP tools
- Khoj AI: Text analysis, database creation
- DuckDuckGo AI: Computational approaches
- Poe Platform: Tool development

### Key Resources

**Programming & Tools**:
- Python Software Foundation - https://python.org
- PostgreSQL Documentation - https://postgresql.org
- MongoDB Documentation - https://mongodb.com
- Neo4j Documentation - https://neo4j.com
- NLTK Project - https://www.nltk.org
- spaCy - https://spacy.io
- BeautifulSoup & Scrapy - Web scraping libraries

**Recommended Books**:
- "The Upanishads" by Eknath Easwaran (Nilgiri Press)
- "The Bhagavata Purana" by Bibek Debroy (Penguin)
- "The Rust Programming Language" by Steve Klabnik, Carol Nichols
- "The Go Programming Language" by Alan Donovan, Brian Kernighan

**Academic Resources**:
- Digital Humanities best practices
- Sanskrit NLP research papers
- Graph database optimization guides
- Web scraping ethics guidelines

### Copyright & Attribution
- All Sanskrit texts from public domain (>70 years old) or openly licensed sources
- Proper attribution maintained for all source repositories
- Compliance with robots.txt for web scraping
- Creative Commons and GPL licenses respected

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Open Source Commitment
This project is committed to open-source principles:
- Free to use, modify, and distribute
- Contributions welcome from the community
- Tools designed for reusability
- Documentation provided for transparency

---

## 👤 Contact

**Project Maintainer**: Sumit Das

**Project Repository**: [https://github.com/RustyNails8/Code4Ved](https://github.com/RustyNails8/Code4Ved)

**Issues & Support**: Please use GitHub Issues for bug reports, feature requests, and questions.

**Discussions**: Join the discussion on GitHub Discussions for general questions and community interaction.

---

## 🙏 Acknowledgments

- All AI assistants consulted during research phase (April 2025)
- Sanskrit text repository maintainers for preserving ancient wisdom
- Open-source community for tools and libraries
- Academic institutions maintaining high-quality text databases
- Digital Humanities community for methodological guidance

---

## 📊 Project Stats

- **Started**: April 2025
- **Status**: Active Development
- **Primary Language**: Python
- **Database Systems**: 3 (PostgreSQL, MongoDB, Neo4j)
- **Text Sources**: 15+ websites
- **Target Texts**: 100+ documents
- **Target Concepts**: 100-200 unique concepts
- **Target Graph Relationships**: 1000-5000 edges

---

## 🎓 Educational Value

This project serves as:
- **Learning Platform**: Hands-on experience with modern data engineering
- **Skill Development**: Python, SQL, NLP, web scraping, graph databases
- **Cultural Bridge**: Connecting ancient philosophy with modern technology
- **Portfolio Project**: Demonstrable work for career advancement
- **Community Contribution**: Open-source tools for Sanskrit studies
- **Interdisciplinary Study**: Philosophy, spirituality, computer science, linguistics

---

**Made with ❤️ for ancient wisdom and modern technology**

---

*Last Updated: October 4, 2025*
```

This comprehensive README.md collates information from all the specified files including:
- Project charter details (charter.md)
- Business case and justification (business_case.md)
- Stakeholder information (stakeholders.md)
- Research findings from daily notes (external data files)
- Technical specifications (FSD.md, data_model.md)
- Risk register (risk_register_plan.md)
- References and resources (references.md)

The README provides a complete overview of the Code4Ved project suitable for GitHub and project documentation purposes.