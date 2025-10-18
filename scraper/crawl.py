# scraper/crawl.py
import hashlib
import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import Iterator, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models import DocumentMeta

# Config from env (simple)
MAX_PAGES = int(os.getenv("SCRAPER_MAX_PAGES", "10"))
SEED_URLS = os.getenv("SCRAPER_SEED_URLS", "https://mospi.gov.in/").split(",")
RATE_LIMIT = float(os.getenv("SCRAPER_RATE_SECONDS", "1.0"))
USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "MoSPI-Scraper/0.1 (+you@example.com)")

DB_PATH = os.getenv("SCRAPER_DB_PATH", "data/raw/scraper.db")

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("scraper")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        title TEXT,
        url TEXT UNIQUE,
        date_published TEXT,
        summary TEXT,
        category TEXT,
        hash TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)
    conn.commit()
    return conn

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def fetch_url(url: str) -> requests.Response:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp

def parse_listing(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    # heuristic: links under a content list
    links = []
    for a in soup.select("a"):
        href = a.get("href")
        if not href:
            continue
        full = urljoin(base_url, href)
        # simple filter - same domain
        if base_url.split("/")[2] in full:
            links.append(full)
    # dedupe preserve order
    seen = set()
    out = []
    for l in links:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return out

def parse_detail(html: str, url: str) -> DocumentMeta:
    soup = BeautifulSoup(html, "html.parser")
    #title = (soup.find("h1") or soup.find("title")).get_text(strip=True)
    title_el = soup.find("h1") or soup.find("title")
    title = title_el.get_text(strip=True) if title_el else "Untitled Document"

    # date tries
    date_text = None
    for sel in ["time", ".date", ".posted-on"]:
        el = soup.select_one(sel)
        if el:
            date_text = el.get_text(strip=True)
            break
    summary_el = soup.select_one("meta[name='description']")
    summary = summary_el.get("content") if summary_el else None
    # file links like pdfs
    file_links = []
    for a in soup.select("a"):
        href = a.get("href")
        if href and href.lower().endswith(".pdf"):
            file_links.append(urljoin(url, href))
    # fallback category
    category = None
    return DocumentMeta(id=None, title=title, url=url,
                        date_published=None, summary=summary,
                        category=category, hash="", file_links=file_links)

def crawl_once(seed_urls: Iterator[str], max_pages=MAX_PAGES):
    conn = init_db()
    cur = conn.cursor()
    to_visit = list(seed_urls)
    visited = set()
    pages = 0
    while to_visit and pages < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            resp = fetch_url(url)
        except Exception as e:
            logger.error(json.dumps({"level":"error","msg":"fetch_failed","url":url,"error":str(e)}))
            continue
        visited.add(url)
        pages += 1
        html = resp.text
        # if this looks like a listing page, harvest links
        links = parse_listing(html, url)
        # enqueue detail links
        for l in links:
            if l not in visited and len(visited)+len(to_visit) < max_pages*2:
                to_visit.append(l)
        # If detail page, attempt parse
        doc = parse_detail(html, url)
        # compute hash
        h = sha256_bytes(resp.content)
        doc.hash = h
        # upsert into sqlite
        try:
            cur.execute("INSERT OR IGNORE INTO documents (title,url,date_published,summary,category,hash) VALUES (?,?,?,?,?,?)",
                        (doc.title, doc.url, None, doc.summary, doc.category, doc.hash))
            conn.commit()
            logger.info(json.dumps({"level":"info","event":"doc_saved","url":doc.url}))
        except Exception as e:
            logger.error(json.dumps({"level":"error","msg":"db_write","url":url,"error":str(e)}))
        # rate limit
        time.sleep(RATE_LIMIT)
    conn.close()

if __name__ == "__main__":
    crawl_once(SEED_URLS)
