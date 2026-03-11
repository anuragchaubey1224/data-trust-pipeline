# Data Scraping & Trust Scoring System – Assignment Report

## Introduction

In this assignment, I designed and implemented a multi-source data scraping pipeline that collects structured information from different types of online platforms and evaluates the reliability of each source using a rule-based trust scoring system. The objective of this project was to build a system capable of extracting content from multiple platforms, structuring the extracted information into a standardized format, and estimating the credibility of each source using defined scoring logic.

The system collects data from three different types of sources: blog posts, YouTube videos, and PubMed research articles. The extracted data is processed, enriched with metadata and topic tags, and finally stored in structured JSON files.

---

## Scraping Strategy

To collect data from different types of platforms, I implemented separate scraping modules for each source type. Each scraper extracts relevant metadata and content while handling the unique structure of the respective platform.

### Blog Scraping

For blog posts, I used BeautifulSoup and readability-lxml to extract clean article text from HTML pages. The blog scraping pipeline follows a multi-stage extraction strategy. First, the HTML document is preprocessed by removing scripts, style tags, navigation menus, and other non-content elements. After preprocessing, additional sanitization removes ads, comment sections, and footer elements that are not part of the main article.

Once the page is cleaned, the readability algorithm is used to extract the primary article content. If the readability extraction fails, the system falls back to extracting text from paragraph tags. This layered approach improves robustness across different blog layouts.

---

### YouTube Scraping

For YouTube videos, I extracted both metadata and textual content. The metadata, including channel name, video title, publish date, and description, is collected using the yt-dlp library. In addition to metadata, the system attempts to fetch the full transcript of the video using the YouTube Transcript API.

If the transcript is not available, the system falls back to using the video description as textual content. This ensures that some content is always available for further processing such as topic tagging and chunking.

---

### PubMed Scraping

For scientific articles, I used the NCBI E-utilities API provided by PubMed. The pipeline performs API requests to retrieve article information such as title, authors, journal name, publication year, and abstract.

The response from the API is returned in XML format, which is parsed using the lxml library to extract the required fields. The system also respects PubMed’s rate limits by restricting requests to a safe frequency.

---

## Topic Tagging Method

To automatically identify the topics discussed in each source, I implemented a keyword extraction method using KeyBERT. KeyBERT leverages transformer-based sentence embeddings to identify the most relevant keywords from the content.

The algorithm extracts the top five keywords or key phrases from the content using semantic similarity scoring. These keywords serve as topic tags and provide a concise representation of the main themes of the article or video.

---

## Content Chunking Strategy

Long textual content is split into smaller segments to make downstream processing easier. I implemented a fixed-size chunking strategy where the content is divided into chunks of approximately 300 words with a small overlap between consecutive chunks.

The overlap helps preserve contextual continuity between chunks and ensures that important information is not lost at chunk boundaries. This approach is particularly useful when preparing content for search systems or machine learning pipelines.

---

## Trust Score Algorithm

To evaluate the reliability of each source, I designed a rule-based trust scoring system. The trust score ranges from 0 to 1 and is calculated using a weighted combination of several credibility factors.

The final trust score is computed using the following factors:

* Author credibility
* Citation quality
* Domain authority
* Content recency
* Presence of medical disclaimers

Each factor contributes to the final score using predefined weights. For example, author credibility and domain authority contribute positively to the score, while missing citations or outdated content reduce the trust score.

The rule-based approach was chosen because it is transparent, easy to interpret, and does not require training data.

---

## Edge Case Handling

The system includes several mechanisms to handle common edge cases that occur during scraping and processing.

If author information is missing, the system assigns a neutral credibility score rather than failing. When publication dates are unavailable, a fallback value is used to maintain scoring consistency. For YouTube videos without transcripts, the system uses the video description as an alternative text source.

The pipeline also supports non-English content using automatic language detection. Additionally, long articles are automatically chunked to avoid memory issues during processing.

---

## Abuse Prevention Logic

The trust scoring system also includes safeguards against potential manipulation or misleading content. For example, domains with low authority are penalized to reduce the impact of spam blogs. Medical content without proper disclaimers receives a significant penalty in the scoring system.

The algorithm also discourages outdated information by applying recency penalties to older content. These safeguards help ensure that unreliable sources receive lower trust scores.

---

## Limitations

Although the system performs well for the selected sources, there are several limitations. The scraper does not support JavaScript-rendered websites because it does not use browser automation tools such as Selenium or Playwright. In addition, YouTube transcripts are only available when captions are enabled by the content creator.

The trust scoring algorithm currently relies on heuristic rules rather than real citation databases or fact-checking systems. Furthermore, the pipeline processes sources sequentially and stores data in JSON files, which may limit scalability for very large datasets.

---

## Conclusion

In this project, I successfully implemented a multi-source scraping pipeline capable of collecting structured content from blogs, YouTube videos, and PubMed articles. The pipeline automatically extracts metadata, generates topic tags, splits content into chunks, and assigns a trust score to each source using a rule-based scoring algorithm.

The system demonstrates how automated data collection and credibility evaluation can be combined into a unified pipeline. While the current implementation is suitable for small-scale data collection, it can be extended in the future with machine learning models, external credibility APIs, and distributed processing to support larger production systems.
