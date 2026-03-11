#!/usr/bin/env python3
"""
Split unified output JSON into separate files by source type.

NOTE: As of the latest version, the pipeline automatically creates
split files (blogs.json, youtube.json, pubmed.json) when running
pipeline/run_pipeline.py. This utility is kept for manual splitting
if needed.

This script splits output/scraped_data.json into:
- output/blogs.json (blog articles)
- output/youtube.json (YouTube videos)
- output/pubmed.json (PubMed articles)

Usage:
    python3 utils/split_output.py
"""

import json
import os
from pathlib import Path


def split_output():
    """Split unified JSON output into separate files by source type."""
    
    # Input file
    input_file = Path('output/scraped_data.json')
    
    # Check if input exists
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found")
        print("   Run the pipeline first: python3 pipeline/run_pipeline.py")
        return
    
    # Load unified data
    print(f"📖 Reading {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print(f"   Loaded {len(data)} sources")
    
    # Split by source type
    blogs = [item for item in data if item['source_type'] == 'blog']
    youtube = [item for item in data if item['source_type'] == 'youtube']
    pubmed = [item for item in data if item['source_type'] == 'pubmed']
    
    # Write separate files
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    files_written = []
    
    if blogs:
        blogs_file = output_dir / 'blogs.json'
        with open(blogs_file, 'w') as f:
            json.dump(blogs, f, indent=2, ensure_ascii=False)
        files_written.append(f"blogs.json ({len(blogs)} sources)")
        print(f"✅ Created {blogs_file}")
    
    if youtube:
        youtube_file = output_dir / 'youtube.json'
        with open(youtube_file, 'w') as f:
            json.dump(youtube, f, indent=2, ensure_ascii=False)
        files_written.append(f"youtube.json ({len(youtube)} sources)")
        print(f"✅ Created {youtube_file}")
    
    if pubmed:
        pubmed_file = output_dir / 'pubmed.json'
        with open(pubmed_file, 'w') as f:
            json.dump(pubmed, f, indent=2, ensure_ascii=False)
        files_written.append(f"pubmed.json ({len(pubmed)} sources)")
        print(f"✅ Created {pubmed_file}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Split Summary:")
    print("="*60)
    for item in files_written:
        print(f"   • {item}")
    
    print(f"\n✨ Total: {len(data)} sources split into {len(files_written)} files")
    print("\n📁 Output directory: output/")
    print("   Files ready for submission:")
    print("   • output/blogs.json")
    print("   • output/youtube.json") 
    print("   • output/pubmed.json")
    print("   • output/scraped_data.json (unified)")


if __name__ == '__main__':
    print("="*60)
    print("🔀 JSON Output Splitter")
    print("="*60)
    split_output()
