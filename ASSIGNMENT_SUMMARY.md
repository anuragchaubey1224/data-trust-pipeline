# Assignment Summary - Data Trust Pipeline
  
**Project:** Multi-Source Data Scraping & Trust Scoring System

## Objective

Design and implement a production-ready data scraping pipeline that extracts structured content from multiple platforms and evaluates source reliability using a trust scoring algorithm.

---

## Task 1: Multi-Source Web Scraper

### Implementation Summary

**Scraped Sources:**
- ✅ 3 Blog Posts (IBM, W3Schools, GeeksforGeeks)
- ✅ 2 YouTube Videos (3Blue1Brown, freeCodeCamp.org)
- ✅ 1 PubMed Article (PMID: 31452104)

**Technology Stack:**
- **Blogs**: BeautifulSoup4 + readability-lxml for clean HTML parsing
- **YouTube**: yt-dlp for metadata + youtube-transcript-api for transcripts
- **PubMed**: NCBI E-utilities API with XML parsing


## Tools & Libraries Used

- **HTTP**: requests + certifi (SSL)
- **HTML Parsing**: BeautifulSoup4 + lxml + readability-lxml
- **YouTube**: yt-dlp + youtube-transcript-api
- **XML Parsing**: lxml (PubMed API responses)
- **NLP**: langdetect (language detection)
- **Keyword Extraction**: KeyBERT + sentence-transformers
- **Configuration**: PyYAML
- **Testing**: Custom test suite (test_all.py)



### Scraping Strategy

**1. Blog Scraper** - 4-Phase Extraction:
- Phase 1: HTML preprocessing (remove scripts, styles, navigation)
- Phase 2: Sanitization (remove ads, comments, footers)
- Phase 3: Readability extraction (article-focused content)
- Phase 4: Fallback to manual <p> tag extraction

**2. YouTube Scraper** - Metadata + Transcript:
- Extract channel, title, publish date, and description via yt-dlp
- Fetch full transcript using YouTube Transcript API
- Fallback to description if transcript unavailable

**3. PubMed Scraper** - API Integration:
- REST API calls to NCBI E-utilities (ESearch + EFetch)
- XML parsing for title, authors, journal, year, and abstract
- Rate limit compliant (3 requests/second, free tier)

### Metadata Extraction

All sources extract:
- ✅ Author/publisher name
- ✅ Publication date (ISO format or year)
- ✅ Page title or video title
- ✅ Full content (article text, transcript, or abstract)

### Automatic Topic Tagging

**Method:** KeyBERT (BERT-based keyword extraction)
- Uses sentence-transformers for semantic embeddings
- Extracts top 5 bi-gram keywords per source
- Cosine similarity scoring for relevance

**Example output:**
```json
"topic_tags": ["machine learning", "neural networks", "deep learning", "python programming", "data science"]
```

### Content Chunking

**Strategy:** Overlapping fixed-size chunks
- Chunk size: 300 words
- Overlap: 50 words (16.6%)
- Preserves context across boundaries
- Handles short content gracefully

**Example:**
```json
"content_chunks": [
  "Introduction to machine learning concepts...",
  "...continued discussion about supervised learning...",
  "...applications in healthcare and finance..."
]
```

### Data Storage

**Output Format:** Standardized JSON schema
```json
{
  "source_url": "https://...",
  "source_type": "blog | youtube | pubmed",
  "author": "Author Name",
  "published_date": "2024-03-10",
  "language": "en",
  "region": "global",
  "topic_tags": ["keyword1", "keyword2", ...],
  "trust_score": 0.65,
  "content_chunks": ["chunk1", "chunk2", ...]
}
```

**File Structure:**
- `output/scraped_data.json` - Unified file (all 6 sources)
- `output/blogs.json` - Blog sources only
- `output/youtube.json` - YouTube sources only
- `output/pubmed.json` - PubMed sources only

---

## Task 2: Trust Score System Design

### Algorithm Design

**Formula:**
```
Trust Score = (0.25 × AuthorCredibility) + (0.20 × CitationQuality) + 
              (0.20 × DomainAuthority) + (0.20 × Recency) + 
              (0.15 × MedicalDisclaimer)
```

**Output Range:** 0.0 (untrustworthy) to 1.0 (highly credible)

### Scoring Factors

**1. Author Credibility (25% weight)**
- PhD/Dr credentials: 0.9
- Multiple authors: averaged score
- No author: 0.3 (neutral penalty)

**2. Citation Quality (20% weight)**
- Research keywords detected: study, research, data, evidence
- High citations (10+): 0.9
- No citations: 0.3

**3. Domain Authority (20% weight)**
- PubMed/academic: 0.9
- Educational sites (.edu): 0.7
- YouTube: 0.5
- Unknown: 0.3

**4. Content Recency (20% weight)**
- <1 year: 1.0
- 3-5 years: 0.6
- >10 years: 0.2

**5. Medical Disclaimer (15% weight)**
- Medical content without disclaimer: 0.0 (critical penalty)
- Has disclaimer: 0.8
- Non-medical: 0.4 (neutral)

### Edge Cases Handled

**1. Missing Metadata**
- Missing author → Use neutral score (0.3)
- Missing date → Use current year
- Missing transcript → Use video description

**2. Multiple Authors**
- Average credibility scores across all co-authors
- Prevents single bad actor from dominating

**3. Non-English Content**
- Automatic language detection via langdetect
- Supports 55+ languages
- Continues processing for all languages

**4. Long Articles**
- Chunking into 300-word segments
- Maintains processing efficiency
- Prevents memory overload

**5. Anti-Scraping Protection**
- Retry logic with exponential backoff
- SSL certificate handling for macOS
- User-agent and header management
- Use Proxy ip for strict websites

### Abuse Prevention

**Fake Authors**
- Pattern matching with content quality validation
- Multiple author averaging prevents gaming

**SEO Spam Blogs**
- Domain reputation scoring penalizes unknown domains
- Citation quality must align with domain claims

**Misleading Medical Content**
- Critical 0.0 penalty for medical topics without disclaimers
- Keyword-based medical content detection

**Outdated Information**
- Strong recency decay prevents obsolete content promotion
- >10 years = 0.2 maximum score

### Trust Score: Assignment vs Industry

**Assignment Approach (Implemented):**
- Rule-based heuristic scoring
- 5 credibility factors with fixed weights

**Industry Production Systems:**
- Machine learning models (e.g., Google's E-A-T)
- Citation graph analysis (e.g., Google Scholar)
- External API verification (ORCID for authors, CrossRef for citations)
- Human fact-checker integration (NewsGuard model)

**Why Rule-Based for This Assignment:**
1. Transparent and explainable (critical for medical content)
2. No training data required (greenfield project)
3. Fast execution (<1ms per source)

**Production Upgrade Path:**
- Integrate CrossRef API for real citation counting
- Add ORCID author verification
- Implement ML-based fact-checking (post-MVP)
- Build domain reputation database with feedback loop


---

## Performance Metrics

**Test Run (6 sources):**
- Processing time: 22.45 seconds
- Words processed: 70,098 words
- Chunks generated: 282 chunks
- Success rate: 100% (6/6 sources)

**Per-Source Timing:**
- Blogs: 2-5 seconds
- YouTube: 3-8 seconds
- PubMed: 1-2 seconds

---

## Project Limitations

**Scraping:**
- No support for JavaScript-rendered sites (requires Selenium/Playwright)
- YouTube transcripts depend on content creator enabling captions
- PubMed rate limited to 3 requests/second (free tier)

**Processing:**
- Language detection less accurate for short text (<50 words)
- Topic tagging requires 420MB model download on first run but handled using proper UX
- Fixed 300-word chunk size (not configurable via config)

**Trust Scoring:**
- Simple pattern matching for author credentials (not comprehensive)
- Limited hardcoded domain reputation list
- No true citation counting (keyword-based only)
- No fact-checking or content verification

**Scalability:**
- Sequential processing (no parallelization)
- No caching (re-scrapes on every run)
- JSON file storage only (not suitable for large-scale data)
- All data loaded in memory before writing

---

## How to Run

**Setup:**
```bash
python3 -m venv venv_data
source venv_data/bin/activate
pip install -r requirements.txt
```

**Verify Installation:**
```bash
python3 test_all.py
# Expected: ✓ ALL TESTS PASSED (5/5)
```

**Run Pipeline:**
```bash
python3 pipeline/run_pipeline.py
# Output: 4 JSON files in output/ directory
```

---

## Deliverables

✅ **Source Code**: Complete modular pipeline with 9 core modules  
✅ **Output Dataset**: 4 JSON files (unified + 3 source-specific files)  
✅ **Documentation**: README.md, QUICKSTART.md, EDGE_CASES.md  
✅ **Test Suite**: Master test suite + 9 individual component tests  
  