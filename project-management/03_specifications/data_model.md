# Data Model Specification

## Document Information
**Project**: Code4Ved - Vedic Texts Analysis Platform
**Version**: 1.0
**Date**: 2025-10-04
**Author**: Sumit Das

## Conceptual Data Model

The Code4Ved platform uses a multi-database architecture:

1. **PostgreSQL** - Relational database for structured metadata and relationships
2. **MongoDB** - Document database for unstructured annotations and commentary
3. **Neo4j** - Graph database for philosophical concept relationships

### High-Level Entity Relationships

```
Texts (1) ─────── (M) Text_Concepts ─────── (M) Concepts
  │                                              │
  │                                              │
  └─── (M) Text_Themes ─────── (M) Themes       │
                                                  │
                                         (Graph) Concept_Relationships
                                                  │
                                         (Graph) Scientific_Topics
```

## Logical Data Model

### Entity: Text
**Description**: Represents a single Vedic/Sanskrit text document

| Attribute | Type | Length | Required | Description |
|-----------|------|--------|----------|-------------|
| id | SERIAL | - | Yes | Unique identifier (primary key) |
| title | VARCHAR | 500 | Yes | Title of the text |
| language | VARCHAR | 50 | Yes | Language (English/Hindi/Sanskrit) |
| format | VARCHAR | 50 | Yes | Source format (PDF/HTML/text) |
| category | VARCHAR | 100 | Yes | Category (Vedas/Puranas/Upanishads/etc) |
| subcategory | VARCHAR | 100 | No | Specific subcategory (e.g., Rigveda, Yajurveda) |
| source_url | TEXT | - | Yes | Original source URL |
| source_website | VARCHAR | 200 | Yes | Website name for attribution |
| extracted_date | TIMESTAMP | - | Yes | Date text was extracted |
| content | TEXT | - | Yes | Full text content |
| content_hash | VARCHAR | 64 | Yes | SHA-256 hash for duplicate detection |
| word_count | INTEGER | - | No | Total words in text |
| created_at | TIMESTAMP | - | Yes | Record creation timestamp |
| updated_at | TIMESTAMP | - | No | Last update timestamp |

**Business Rules**:
- Title must be unique per category
- Content_hash used to detect duplicate texts from different sources
- Source_url must be valid HTTP/HTTPS URL
- Language must be one of: English, Hindi, Sanskrit, Mixed

**Relationships**:
- One text can have many concepts (Text_Concepts)
- One text can have many themes (Text_Themes)
- One text can have many annotations (MongoDB)
- One text can be referenced in many graph relationships (Neo4j)

### Entity: Philosophical_Concept
**Description**: Represents a philosophical or spiritual concept from Vedic literature

| Attribute | Type | Length | Required | Description |
|-----------|------|--------|----------|-------------|
| id | SERIAL | - | Yes | Unique identifier |
| concept_name | VARCHAR | 200 | Yes | Name of concept (unique) |
| sanskrit_term | VARCHAR | 200 | No | Original Sanskrit term |
| description | TEXT | - | No | Description of concept |
| category | VARCHAR | 100 | No | Concept category (metaphysical/ethical/etc) |
| created_at | TIMESTAMP | - | Yes | Record creation timestamp |

**Business Rules**:
- Concept_name must be unique
- Sanskrit_term should use IAST transliteration
- Core concepts: Atman, Brahman, Karma, Dharma, Moksha, Maya, Yoga, Bhakti

**Relationships**:
- One concept can appear in many texts (Text_Concepts)
- One concept can relate to many other concepts (Neo4j graph)
- One concept can connect to scientific topics (Neo4j graph)

### Entity: Theme
**Description**: Represents thematic categories for texts

| Attribute | Type | Length | Required | Description |
|-----------|------|--------|----------|-------------|
| id | SERIAL | - | Yes | Unique identifier |
| theme_name | VARCHAR | 200 | Yes | Name of theme (unique) |
| description | TEXT | - | No | Theme description |
| created_at | TIMESTAMP | - | Yes | Record creation timestamp |

**Business Rules**:
- Theme_name must be unique
- Themes include: Spirituality, Philosophy, War, Medicine, Mathematics, Art, Duty, Ritual, Cosmology

**Relationships**:
- One theme can be associated with many texts (Text_Themes)

### Entity: Text_Concept
**Description**: Junction table linking texts to concepts with context

| Attribute | Type | Length | Required | Description |
|-----------|------|--------|----------|-------------|
| text_id | INTEGER | - | Yes | Foreign key to Texts |
| concept_id | INTEGER | - | Yes | Foreign key to Philosophical_Concepts |
| occurrence_count | INTEGER | - | No | Number of times concept appears |
| context | TEXT | - | No | Surrounding text context |
| confidence | FLOAT | - | No | Confidence score (0.0-1.0) for automated extraction |
| is_manual | BOOLEAN | - | Yes | True if manually tagged, false if automated |
| created_at | TIMESTAMP | - | Yes | Record creation timestamp |

**Business Rules**:
- Composite primary key (text_id, concept_id)
- Confidence score between 0.0 and 1.0
- Manual tags override automated tags

### Entity: Text_Theme
**Description**: Junction table linking texts to themes

| Attribute | Type | Length | Required | Description |
|-----------|------|--------|----------|-------------|
| text_id | INTEGER | - | Yes | Foreign key to Texts |
| theme_id | INTEGER | - | Yes | Foreign key to Themes |
| relevance_score | FLOAT | - | No | How central this theme is (0.0-1.0) |
| created_at | TIMESTAMP | - | Yes | Record creation timestamp |

**Business Rules**:
- Composite primary key (text_id, theme_id)
- Relevance score between 0.0 and 1.0

### Entity: Scraping_Log
**Description**: Audit trail of web scraping activities

| Attribute | Type | Length | Required | Description |
|-----------|------|--------|----------|-------------|
| id | SERIAL | - | Yes | Unique identifier |
| url | TEXT | - | Yes | URL accessed |
| timestamp | TIMESTAMP | - | Yes | Access timestamp |
| status_code | INTEGER | - | No | HTTP status code |
| success | BOOLEAN | - | Yes | Scraping success/failure |
| error_message | TEXT | - | No | Error details if failed |
| user_agent | VARCHAR | 500 | Yes | User agent string used |

**Business Rules**:
- Log all scraping attempts regardless of success
- Retain logs for audit and troubleshooting

## Physical Data Model - PostgreSQL

### Database Schema (PostgreSQL)

```sql
-- Create database
CREATE DATABASE code4ved;

-- Connect to database
\c code4ved

-- Texts table
CREATE TABLE texts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    language VARCHAR(50) NOT NULL CHECK (language IN ('English', 'Hindi', 'Sanskrit', 'Mixed')),
    format VARCHAR(50) NOT NULL CHECK (format IN ('PDF', 'HTML', 'Text')),
    category VARCHAR(100) NOT NULL CHECK (category IN ('Vedas', 'Puranas', 'Upanishads', 'Samhitas', 'Epic Poems', 'Other')),
    subcategory VARCHAR(100),
    source_url TEXT NOT NULL,
    source_website VARCHAR(200) NOT NULL,
    extracted_date TIMESTAMP NOT NULL,
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL UNIQUE,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Philosophical concepts table
CREATE TABLE philosophical_concepts (
    id SERIAL PRIMARY KEY,
    concept_name VARCHAR(200) NOT NULL UNIQUE,
    sanskrit_term VARCHAR(200),
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Themes table
CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    theme_name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Text-Concept junction table
CREATE TABLE text_concepts (
    text_id INTEGER NOT NULL REFERENCES texts(id) ON DELETE CASCADE,
    concept_id INTEGER NOT NULL REFERENCES philosophical_concepts(id) ON DELETE CASCADE,
    occurrence_count INTEGER DEFAULT 1,
    context TEXT,
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    is_manual BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (text_id, concept_id)
);

-- Text-Theme junction table
CREATE TABLE text_themes (
    text_id INTEGER NOT NULL REFERENCES texts(id) ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    relevance_score FLOAT CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (text_id, theme_id)
);

-- Scraping log table
CREATE TABLE scraping_log (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_code INTEGER,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    user_agent VARCHAR(500) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_texts_category ON texts(category);
CREATE INDEX idx_texts_language ON texts(language);
CREATE INDEX idx_texts_source_website ON texts(source_website);
CREATE INDEX idx_texts_content_hash ON texts(content_hash);
CREATE INDEX idx_text_concepts_concept_id ON text_concepts(concept_id);
CREATE INDEX idx_text_themes_theme_id ON text_themes(theme_id);
CREATE INDEX idx_scraping_log_timestamp ON scraping_log(timestamp);

-- Full-text search index
CREATE INDEX idx_texts_content_fts ON texts USING gin(to_tsvector('english', content));
CREATE INDEX idx_texts_title_fts ON texts USING gin(to_tsvector('english', title));
```

### Indexes and Constraints

**Primary Indexes**:
- All tables have primary key indexes (auto-created)
- Composite primary keys on junction tables

**Secondary Indexes**:
- Category, language, source_website for filtering
- Content_hash for duplicate detection
- Foreign keys for join performance
- Full-text search indexes for content and title

**Constraints**:
- CHECK constraints on enumerations (language, format, category)
- UNIQUE constraints on content_hash, concept_name, theme_name
- FOREIGN KEY constraints with CASCADE delete
- NOT NULL constraints on required fields

## Physical Data Model - MongoDB

### Collection: annotations

**Purpose**: Store freeform annotations, commentary, and user notes

```json
{
  "_id": ObjectId("..."),
  "text_id": 123,  // References PostgreSQL texts.id
  "annotations": [
    {
      "annotation_id": "uuid-v4",
      "created_at": ISODate("2025-01-01T10:00:00Z"),
      "updated_at": ISODate("2025-01-01T10:00:00Z"),
      "type": "commentary",  // commentary, note, translation, question
      "content": "This verse discusses the nature of Atman...",
      "author": "self",
      "tags": ["atman", "metaphysics", "upanishad"],
      "verse_reference": "Chapter 2, Verse 15",
      "language": "English"
    }
  ],
  "metadata": {
    "total_annotations": 1,
    "last_updated": ISODate("2025-01-01T10:00:00Z")
  }
}
```

**Indexes**:
```javascript
db.annotations.createIndex({ "text_id": 1 });
db.annotations.createIndex({ "annotations.tags": 1 });
db.annotations.createIndex({ "annotations.type": 1 });
db.annotations.createIndex({ "annotations.created_at": -1 });
```

## Physical Data Model - Neo4j

### Graph Schema

**Node Types**:

1. **PhilosophicalConcept**
   ```cypher
   (:PhilosophicalConcept {
     concept_id: INT,  // From PostgreSQL
     name: STRING,
     sanskrit_term: STRING,
     category: STRING
   })
   ```

2. **ScientificTopic**
   ```cypher
   (:ScientificTopic {
     topic_id: STRING,
     name: STRING,
     field: STRING  // physics, mathematics, quantum_mechanics, etc.
   })
   ```

3. **Text**
   ```cypher
   (:Text {
     text_id: INT,  // From PostgreSQL
     title: STRING,
     category: STRING
   })
   ```

**Relationship Types**:

1. **RELATES_TO** (Concept → Concept)
   ```cypher
   (:PhilosophicalConcept)-[:RELATES_TO {
     strength: FLOAT,  // 0.0-1.0
     cooccurrence_count: INT,
     relationship_type: STRING  // similar, opposite, subset, superset
   }]->(:PhilosophicalConcept)
   ```

2. **CONNECTS_TO** (Concept → Scientific Topic)
   ```cypher
   (:PhilosophicalConcept)-[:CONNECTS_TO {
     connection_strength: FLOAT,
     evidence_text: STRING,
     verified: BOOLEAN
   }]->(:ScientificTopic)
   ```

3. **MENTIONED_IN** (Concept → Text)
   ```cypher
   (:PhilosophicalConcept)-[:MENTIONED_IN {
     occurrence_count: INT,
     prominence: FLOAT  // 0.0-1.0
   }]->(:Text)
   ```

**Sample Cypher Queries**:

```cypher
// Create concept nodes
CREATE (:PhilosophicalConcept {
  concept_id: 1,
  name: 'Atman',
  sanskrit_term: 'आत्मन्',
  category: 'metaphysical'
});

// Create relationships
MATCH (a:PhilosophicalConcept {name: 'Atman'}),
      (b:PhilosophicalConcept {name: 'Brahman'})
CREATE (a)-[:RELATES_TO {
  strength: 0.95,
  cooccurrence_count: 45,
  relationship_type: 'closely_related'
}]->(b);

// Query related concepts
MATCH (c:PhilosophicalConcept {name: 'Karma'})-[r:RELATES_TO]->(related)
RETURN related.name, r.strength
ORDER BY r.strength DESC
LIMIT 10;
```

## Data Dictionary

### Complete Field Reference

**texts.category values**:
- Vedas: Rigveda, Yajurveda, Samaveda, Atharvaveda
- Upanishads: Principal Upanishads, Minor Upanishads
- Puranas: Mahapuranas (18), Upapuranas
- Samhitas: Brahmana texts, Aranyakas
- Epic Poems: Mahabharata, Ramayana
- Other: Miscellaneous texts

**philosophical_concepts.category values**:
- Metaphysical: Atman, Brahman, Maya
- Ethical: Dharma, Karma
- Spiritual: Moksha, Yoga, Bhakti
- Epistemological: Pramana, Viveka

**themes.theme_name values**:
- Spirituality, Philosophy, Metaphysics
- Ethics, Duty, Morality
- Ritual, Ceremony, Worship
- Cosmology, Creation, Universe
- Medicine, Healing, Ayurveda
- Mathematics, Astronomy
- War, Strategy, Statecraft
- Art, Music, Dance
- Grammar, Linguistics

## Data Migration and Synchronization

### Cross-Database Synchronization

**PostgreSQL → Neo4j**:
- Text records create Text nodes
- Concept records create PhilosophicalConcept nodes
- Text_Concepts create MENTIONED_IN relationships

**PostgreSQL → MongoDB**:
- Text IDs serve as references in annotations collection
- No direct synchronization needed (reference-based)

**Synchronization Triggers**:
- When new text added to PostgreSQL → create Text node in Neo4j
- When concept extracted → create/update relationships in Neo4j
- Manual annotations always stored in MongoDB first

## Data Quality and Validation

**Validation Rules**:
- All URLs must be valid and accessible
- Content_hash must be unique (prevent duplicates)
- Confidence scores must be 0.0-1.0
- Foreign key integrity enforced
- Required fields cannot be null

**Data Cleansing**:
- Remove HTML tags from extracted text
- Normalize whitespace
- Standardize Sanskrit transliteration (IAST)
- Deduplicate texts by content_hash
