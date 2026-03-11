# Quick Start

Run the complete Data Trust Pipeline in under **3 minutes**.

## 1. Setup Environment

```bash
cd data-trust-pipeline

# Create virtual environment
python3 -m venv venv
        (OR)
python -m venv venv

# Activate environment
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Verify Installation

Before running the full pipeline, verify all components are working:

```bash
python3 test_all.py
```

Expected output:

```
✓ PASS  Configuration
✓ PASS  Blog Scraper
✓ PASS  YouTube Scraper
✓ PASS  PubMed Scraper
✓ PASS  Unified Pipeline

✓ ALL TESTS PASSED (5/5)
```

If all tests pass, you're ready to run the complete pipeline!

---

## 3. Run the Pipeline

```bash
python3 pipeline/run_pipeline.py
```

The pipeline will:

* Scrape **3 blogs, 2 YouTube videos, 1 PubMed article**
* Clean and process content
* Generate topic tags using **KeyBERT**
* Split content into chunks
* Calculate **trust scores**
* Store results as structured JSON

---

## 4. View Output

Output files are generated automatically in the `output/` folder:

```
output/
├── scraped_data.json   # Unified dataset
├── blogs.json          # Blog sources
├── youtube.json        # YouTube sources
└── pubmed.json         # PubMed sources
```

Example:

```bash
cat output/scraped_data.json
```

---

## Output Schema

```json
{
  "source_url": "...",
  "source_type": "blog | youtube | pubmed",
  "author": "...",
  "published_date": "...",
  "language": "en",
  "region": "global",
  "topic_tags": ["keyword1", "keyword2", "..."],
  "trust_score": 0.52,
  "content_chunks": ["chunk1", "chunk2"]
}
```

---

## Documentation

* **README.md** – Project overview and architecture
* **ASSIGNMENT_SUMMARY.md** – Assignment explanation
* **ASSIGNMENT_REPORT.md** – Detailed technical analysis
* **EDGE_CASES.md** – Edge case handling examples

---

**Runtime:** ~22 seconds
**Sources processed:** 6
**Output:** 4 JSON files
