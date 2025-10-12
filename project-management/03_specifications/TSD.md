# Technical Specification Document (TSD)

## Document Information
**Document Title**: Code4Ved Technical Specification  
**Version**: 1.0  
**Date**: 2025-10-04  
**Author**: Sumit Das  
**Technical Reviewers**: Self-Review  
**Status**: Draft

## Executive Summary
Code4Ved is a comprehensive digital platform that combines programming expertise with the study of ancient Indian texts (Vedas, Puranas, Upanishads). The system uses a multi-database architecture with web scraping, NLP analysis, and knowledge graph visualization to create a modern, accessible environment for exploring Vedic literature.

## System Architecture

### High-Level Architecture
```
┌─────────────────────┐
│ Web Scrapers │ ← Python/GoLang/Rust
│ (BeautifulSoup) │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Data Processing │ ← PyPDF2, text cleaning
│ & Extraction │
└──────────┬──────────┘
│
▼
┌─────────────────────────────────────┐
│ Database Layer │
│ ┌─────────┬─────────┬───────────┐ │
│ │PostgreSQL│ MongoDB │ Neo4j │ │
│ │(metadata)│(comments)│ (graph) │ │
│ └─────────┴─────────┴───────────┘ │
└──────────┬──────────────────────────┘
│
▼
┌─────────────────────┐
│ NLP Pipeline │ ← NLTK, spaCy
│ (Analysis) │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Visualization │ ← Mermaid, NetworkX
│ & Query Interface │
└─────────────────────┘
```


### System Components
| Component | Purpose | Technology | Dependencies |
|-----------|---------|------------|--------------|
| Web Scraping Module | Extract texts from repositories | Python/GoLang/Rust, BeautifulSoup/Scrapy | Internet connectivity, target websites |
| Data Processing | Clean and structure extracted data | Python, PyPDF2, pdfminer | Web scraping module |
| PostgreSQL Database | Structured metadata storage | PostgreSQL 13+ | Database server |
| MongoDB Database | Unstructured annotations | MongoDB 4.4+ | Database server |
| Neo4j Database | Concept relationships | Neo4j 4.0+ | Database server |
| NLP Pipeline | Text analysis and concept extraction | Python, NLTK, spaCy | Processed text data |
| Visualization Engine | Generate charts and graphs | Python, Mermaid, NetworkX | Analysis results |

### Deployment Architecture
Single-machine deployment with local databases and development environment. Future cloud deployment possible.

## Technology Stack

### Programming Languages
- **Primary**: Python 3.8+ - Core development language for web scraping, NLP, and data processing
- **Secondary**: GoLang - High-performance concurrent web scraping
- **Tertiary**: Rust - High-performance text processing and system optimization

### Frameworks and Libraries
| Framework/Library | Version | Purpose | License |
|------------------|---------|---------|---------|
| BeautifulSoup | 4.9+ | HTML parsing | MIT |
| Scrapy | 2.5+ | Web scraping framework | BSD |
| requests | 2.25+ | HTTP library | Apache 2.0 |
| PyPDF2 | 3.0+ | PDF text extraction | BSD |
| NLTK | 3.6+ | Natural language processing | Apache 2.0 |
| spaCy | 3.4+ | Advanced NLP | MIT |
| NetworkX | 2.6+ | Graph analysis | BSD |
| Mermaid | Latest | Diagram generation | MIT |
| psycopg2 | 2.9+ | PostgreSQL adapter | LGPL |
| pymongo | 4.0+ | MongoDB driver | Apache 2.0 |
| neo4j | 5.0+ | Neo4j driver | Apache 2.0 |

### Database Systems
- **Primary Database**: PostgreSQL 13+ - Relational metadata
- **Document Database**: MongoDB 4.4+ - Unstructured annotations
- **Graph Database**: Neo4j 4.0+ - Concept relationships
- **Development Database**: SQLite 3.35+ - Local development

### Infrastructure
- **Cloud Provider**: Local development
- **Compute**: Personal development machine (8+ GB RAM, multi-core CPU)
- **Storage**: Local SSD storage (100+ GB)
- **Network**: Internet connectivity for web scraping

## Detailed Component Design

### Component 1: Web Scraping Module

#### Responsibilities
- Extract text content from 15+ Sanskrit repositories
- Handle multiple formats (HTML, PDF, plain text)
- Implement ethical scraping practices
- Log all scraping activities

#### Interfaces
```python
class WebScraper:
    def scrape_website(self, url: str, format: str) -> ScrapedContent
    def extract_pdf_text(self, pdf_path: str) -> str
    def extract_html_text(self, html_content: str) -> str
    def validate_content(self, content: str) -> bool
```

#### Internal Design
- Modular design supporting multiple scraping strategies
- Rate limiting and robots.txt compliance
- Error handling and retry mechanisms
- Content validation and deduplication

#### Data Storage
- Temporary storage during scraping
- Metadata storage in PostgreSQL
- Content storage with source attribution

#### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| rate_limit | 1.0 | Requests per second |
| retry_attempts | 3 | Number of retry attempts |
| timeout | 30 | Request timeout in seconds |
| user_agent | Code4Ved/1.0 | User agent string |

#### Error Handling
- HTTP error handling with appropriate responses
- Network timeout handling
- Content parsing error recovery
- Logging of all errors for debugging

### Component 2: Database Architecture

#### Responsibilities
- Multi-database coordination
- Data synchronization
- Query optimization
- Backup and recovery

#### Interfaces
```python
class DatabaseManager:
    def store_text(self, text: TextData) -> int
    def store_concept(self, concept: ConceptData) -> int
    def create_relationship(self, rel: RelationshipData) -> bool
    def query_texts(self, filters: QueryFilters) -> List[TextData]
```

#### Internal Design
- PostgreSQL for structured metadata
- MongoDB for unstructured annotations
- Neo4j for concept relationships
- Cross-database synchronization

#### Data Storage
- PostgreSQL: texts, concepts, themes, classifications
- MongoDB: annotations, commentary, user notes
- Neo4j: concept relationships, scientific connections

### Component 3: NLP Pipeline

#### Responsibilities
- Text preprocessing and cleaning
- Concept extraction and classification
- Topic modeling and analysis
- Relationship identification

#### Interfaces
```python
class NLPPipeline:
    def extract_concepts(self, text: str) -> List[Concept]
    def classify_text(self, text: str) -> Classification
    def find_relationships(self, concepts: List[Concept]) -> List[Relationship]
    def generate_topics(self, texts: List[str]) -> List[Topic]
```

#### Internal Design
- Multi-stage processing pipeline
- Confidence scoring for automated results
- Manual validation workflow
- Performance optimization

## Database Design

### Conceptual Model

```
Texts (1) ─────── (M) Text_Concepts ─────── (M) Concepts
│ │
│ │
└─── (M) Text_Themes ─────── (M) Themes │
│
(Graph) Concept_Relationships
│
(Graph) Scientific_Topics
```


### Logical Model
- **Texts**: Core text entities with metadata
- **Concepts**: Philosophical concepts from texts
- **Themes**: Thematic classifications
- **Relationships**: Concept-to-concept and concept-to-science connections

### Physical Design

#### Table: texts
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| title | VARCHAR(500) | NOT NULL | Text title |
| language | VARCHAR(50) | NOT NULL | Language (English/Hindi/Sanskrit) |
| format | VARCHAR(50) | NOT NULL | Source format (PDF/HTML/Text) |
| category | VARCHAR(100) | NOT NULL | Category (Vedas/Puranas/Upanishads) |
| content | TEXT | NOT NULL | Full text content |
| source_url | TEXT | NOT NULL | Original source URL |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**Indexes**:
- idx_texts_category: category - For filtering by text type
- idx_texts_language: language - For language-based queries
- idx_texts_content_fts: content - For full-text search

## API Specifications

### REST API Endpoints

#### Endpoint: Get Texts
**URL**: `GET /api/v1/texts`  
**Purpose**: Retrieve texts with optional filtering  
**Authentication**: None (single-user system)

**Request**:
```json
{
  "filters": {
    "category": "Vedas",
    "language": "English",
    "limit": 10
  }
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "texts": [
      {
        "id": 1,
        "title": "Rigveda",
        "category": "Vedas",
        "language": "English",
        "source_url": "https://example.com/rigveda"
      }
    ],
    "total": 1
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid filter parameters
- `500 Internal Server Error`: Database connection issues

#### Endpoint: Extract Concepts
**URL**: `POST /api/v1/analyze/concepts`  
**Purpose**: Extract philosophical concepts from text  
**Authentication**: None

**Request**:
```json
{
  "text_id": 1,
  "text_content": "Sample text content..."
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "concepts": [
      {
        "name": "Atman",
        "confidence": 0.95,
        "context": "The soul is eternal..."
      }
    ]
  }
}
```

## Security Architecture

### Authentication
Single-user system with local database access. No external authentication required.

### Authorization
Developer has full access to all system components. No role-based access control needed.

### Data Protection
- Database encryption at rest
- TLS for all external communications
- Source attribution for all scraped content
- Respect for website terms of service

### Security Controls
| Control | Implementation | Purpose |
|---------|----------------|---------|
| Rate Limiting | 1 request/second per site | Respect website resources |
| User Agent | Code4Ved/1.0 | Identify scraping purpose |
| Robots.txt | Automatic compliance | Respect website policies |
| Error Logging | Comprehensive logging | Security monitoring |

## Performance Specifications

### Performance Requirements
| Metric | Target | Method of Measurement |
|--------|--------|--------------------|
| Response Time | < 5 seconds | Database query timing |
| Throughput | 100 texts/hour | Processing rate |
| Availability | 95% | Uptime monitoring |

### Scalability Design
- Horizontal scaling through multiple scraping processes
- Vertical scaling through resource optimization
- Database partitioning for large datasets

### Caching Strategy
- Redis for frequently accessed data
- File system caching for processed texts
- Database query result caching

## Integration Specifications

### External System Integrations

#### Integration: Sanskrit Text Repositories
**Purpose**: Extract Vedic texts from multiple sources  
**Protocol**: HTTP/HTTPS  
**Authentication**: None (public access)  
**Data Format**: HTML, PDF, plain text  
**Error Handling**: Retry with exponential backoff

**Endpoints Used**:
| Endpoint | Purpose | Frequency |
|----------|---------|-----------|
| vedicheritage.gov.in | Government texts | Daily |
| gretil.sub.uni-goettingen.de | Academic texts | Weekly |
| sanskritdocuments.org | Community texts | Weekly |

## Monitoring and Logging

### Logging Strategy
- Application logs for debugging
- Performance logs for optimization
- Error logs for troubleshooting
- Audit logs for compliance

### Monitoring Points
| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Usage | > 80% | Alert developer |
| Memory Usage | > 8 GB | Alert developer |
| Database Connections | > 50 | Alert developer |
| Error Rate | > 5% | Alert developer |

### Alerting
- Email alerts for critical issues
- Log file monitoring
- Performance dashboard
- Automated health checks

## Development Guidelines

### Coding Standards
- PEP 8 for Python code
- Comprehensive documentation
- Type hints for all functions
- Unit tests for all modules

### Testing Requirements
- **Unit Tests**: 80% code coverage minimum
- **Integration Tests**: All database operations
- **Performance Tests**: Load testing with realistic data

### Code Review Process
- Self-review for all code changes
- Documentation review
- Performance impact assessment
- Security review for external integrations

## Deployment Specifications

### Environments
| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| Development | Local development | SQLite, minimal data |
| Staging | Testing and validation | PostgreSQL, sample data |
| Production | Full deployment | All databases, full dataset |

### Deployment Process
1. Code review and testing
2. Database migration scripts
3. Configuration updates
4. Service restart
5. Health check validation

### Rollback Procedures
- Database backup restoration
- Configuration rollback
- Service restart
- Health check validation

## Configuration Management

### Configuration Files
| File | Purpose | Format |
|------|---------|--------|
| config.yaml | Main configuration | YAML |
| database.conf | Database settings | INI |
| scraping.conf | Scraping parameters | JSON |

### Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://localhost/code4ved |
| MONGODB_URL | MongoDB connection | mongodb://localhost:27017/code4ved |
| NEO4J_URL | Neo4j connection | bolt://localhost:7687 |
| LOG_LEVEL | Logging level | INFO |

## Risk Assessment

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Website Structure Changes | High | Medium | Flexible scrapers, multiple sources |
| Database Performance | Medium | Low | Proper indexing, query optimization |
| NLP Accuracy | Medium | High | Manual validation, multiple approaches |
| Learning Curve | Low | Medium | Progressive learning, documentation |

## Future Considerations
- Cloud deployment for scalability
- Multi-user support with authentication
- Advanced AI/ML integration
- Mobile application development
- API development for external integrations

## Appendices

### Glossary
- **NLP**: Natural Language Processing
- **RAG**: Retrieval-Augmented Generation
- **IAST**: International Alphabet of Sanskrit Transliteration
- **LDA**: Latent Dirichlet Allocation
- **TF-IDF**: Term Frequency-Inverse Document Frequency

### References
- Python Documentation: https://docs.python.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Neo4j Documentation: https://neo4j.com/docs/
- NLTK Documentation: https://www.nltk.org/

### Decision Records
- **ADR-001**: Multi-database architecture decision
- **ADR-002**: Progressive learning approach (Python → GoLang → Rust)
- **ADR-003**: Mermaid for visualization
- **ADR-004**: Ethical web scraping practices