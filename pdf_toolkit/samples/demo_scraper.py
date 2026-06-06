#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper Demo - Portfolio Sample
Shows my web scraping capability with comments and documentation
"""

import httpx
from bs4 import BeautifulSoup
import json
import csv
from pathlib import Path

def scrape_quotes(tag=None, max_pages=3):
    """
    Scrape quotes from a demo website (toscrape.com)
    Shows: pagination, data extraction, error handling
    """
    base_url = "https://quotes.toscrape.com"
    all_quotes = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}/page/{page}/" if page > 1 else base_url
        if tag:
            url = f"{base_url}/tag/{tag}/page/{page}/" if page > 1 else f"{base_url}/tag/{tag}/"
        
        print(f"Scraping page {page}: {url}")
        
        try:
            resp = httpx.get(url, timeout=10.0)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Error: {e}")
            continue
        
        soup = BeautifulSoup(resp.text, "html.parser")
        quotes = soup.select(".quote")
        
        for q in quotes:
            text = q.select_one(".text").text if q.select_one(".text") else ""
            author = q.select_one(".author").text if q.select_one(".author") else ""
            tags = [t.text for t in q.select(".tag")]
            
            all_quotes.append({
                "text": text,
                "author": author,
                "tags": tags
            })
        
        print(f"  Found {len(quotes)} quotes on page {page}")
    
    return all_quotes

def save_as_json(data, filename="quotes.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} quotes to {filename}")

def save_as_csv(data, filename="quotes.csv"):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        for item in data:
            item["tags"] = ", ".join(item["tags"])
            writer.writerow(item)
    print(f"Saved {len(data)} quotes to {filename}")

if __name__ == "__main__":
    print("=== Web Scraper Demo ===")
    print("Scraping quotes.toscrape.com...")
    print()
    
    quotes = scrape_quotes(max_pages=2)
    
    print(f"\nTotal quotes scraped: {len(quotes)}")
    print(f"\nFirst quote: {quotes[0]['text'][:50]}...")
    print(f"Author: {quotes[0]['author']}")
    print(f"Tags: {', '.join(quotes[0]['tags'])}")
    
    save_as_json(quotes)
    save_as_csv(quotes)
    print("\nDemo complete! See quotes.json and quotes.csv")
