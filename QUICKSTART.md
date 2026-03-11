# Quick Start Guide - Data Trust Pipeline

## ⚡ 3-Minute Setup & Verification

### Step 1: Setup Environment
```bash
cd data-trust-pipeline

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Complete Pipeline
```bash
python3 pipeline/run_pipeline.py
```

**Expected Output:**
```
✓ Scraping 6 sources (3 blogs, 2 YouTube, 1 PubMed)
✓ Processing content (cleaning, language detection, topic tagging, chunking)
✓ Calculating trust scores (5-factor weighted algorithm)
✓ Storing results in output/

Pipeline completed in ~22 seconds
Success rate: 100% (6/6 sources)
Total content chunks: 282
```

### Step 3: View Results
```bash
# View unified output
cat output/scraped_data.json

# Or view split outputs by source type
python3 utils/split_output.py
cat output/blogs.json
cat output/youtube.json
cat output/pubmed.json
```

---

## 📊 What Gets Scraped

**Current sources in `config/sources.yaml`:**
- ✅ 3 Blog articles (IBM, GeeksforGeeks, W3Schools)
- ✅ 2 YouTube videos (3Blue1Brown, freeCodeCamp)
- ✅ 1 PubMed article (PMID: 31452104)

**Output Schema (9 fields):**
```json
{
  "source_url": "https://...",
  "source_type": "blog | youtube | pubmed",
  "author": "Author name(s)",
  "published_date": "ISO date or year",
  "language": "en",
  "region": "global",
  "topic_tags": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "trust_score": 0.525,
  "content_chunks": ["chunk1 (300 words)", "chunk2 (300 words)", ...]
}
```

---

## 📖 Documentation

- **[README.md](README.md)** - Complete project documentation
- **[ASSIGNMENT_REPORT.md](ASSIGNMENT_REPORT.md)** - Technical report (algorithms, edge cases)
- **[EDGE_CASES.md](EDGE_CASES.md)** - Real-world edge case examples

---

## ⚙️ Key Features Demonstrated

1. **Multi-Source Scraping**: 3 different scrapers (Blog, YouTube, PubMed)
2. **Trust Scoring**: 5-factor weighted algorithm (author, citations, domain, recency, disclaimer)
3. **Topic Tagging**: KeyBERT + Sentence Transformers (automatic keyword extraction)
4. **Content Chunking**: 300-word chunks with 50-word overlap
5. **Edge Case Handling**: Missing metadata, multiple authors, non-English content, etc.
6. **Production Quality**: Error handling, retry logic, comprehensive logging

---

**Total Time to Verify:** ~3 minutes
**Success Rate:** 100% (6/6 sources)
**Output:** 4 JSON files in `output/` directory

## ⚠️ Troubleshooting

**SSL Certificate Error:**
```python
scraper = BlogScraper(verify_ssl=False)  # For testing only
```

**YouTube Video Has No Transcript:**
- Not all videos have transcripts
- Choose videos with captions enabled

**PubMed Rate Limit:**
- Free tier: 3 requests/second
- Add delays if scraping many articles

---


**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Last Tested:** March 10, 2026
