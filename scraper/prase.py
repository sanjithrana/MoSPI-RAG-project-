# scraper/parse.py
import os
import sqlite3
import hashlib
import json
from urllib.parse import urlparse
import requests
import pdfplumber
import pandas as pd
from crawl import DB_PATH, sha256_bytes
from datetime import datetime
from tqdm import tqdm

PDF_DIR = os.getenv("PDF_DIR", "data/raw/pdf")

os.makedirs(PDF_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def download_file(url: str, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    resp = requests.get(url, headers={"User-Agent":"MoSPI-Scraper/0.1"}, stream=True, timeout=30)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(1024*64):
            if chunk:
                f.write(chunk)

def extract_text_and_tables(pdf_path: str):
    text = ""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
        # try to extract the first tabular area
        try:
            # camelot would be another strategy but may require ghostscript; keep here optional
            # Use pdfplumber's table extraction (basic)
            first_page = pdf.pages[0]
            tbls = first_page.extract_table()
            if tbls:
                # convert to DataFrame
                df = pd.DataFrame(tbls[1:], columns=tbls[0])
                tables.append(df)
        except Exception:
            pass
    return text, tables

def parse_files():
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT id, url FROM documents")
    rows = cur.fetchall()
    for doc_id, url in rows:
        # naive: find pdf links present on page - we saved none in this simple flow. But for robustness:
        # try common pattern: url + .pdf or check the url itself
        if url.lower().endswith(".pdf"):
            pdf_url = url
        else:
            # skip unless you have file_links in DB (not present here)
            continue
        try:
            r = requests.get(pdf_url, timeout=30, headers={"User-Agent":"MoSPI-Scraper/0.1"})
            r.raise_for_status()
            data = r.content
            file_hash = hashlib.sha256(data).hexdigest()
            parsed = urlparse(pdf_url)
            fname = os.path.join(PDF_DIR, f"{doc_id}_{os.path.basename(parsed.path)}")
            with open(fname, "wb") as f:
                f.write(data)
            text, tables = extract_text_and_tables(fname)
            # write a simple files table
            cur.execute("""CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                document_id INTEGER,
                file_url TEXT,
                file_path TEXT,
                file_hash TEXT,
                file_type TEXT,
                pages INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            )""")
            cur.execute("INSERT INTO files (document_id,file_url,file_path,file_hash,file_type,pages) VALUES (?,?,?,?,?,?)",
                        (doc_id, pdf_url, fname, file_hash, "pdf", 0))
            conn.commit()
            # optional: save extracted text to parquet
            txt_path = fname + ".parquet"
            df = pd.DataFrame([{"document_id":doc_id, "text": text}])
            df.to_parquet(txt_path, index=False)
            print("Parsed", fname)
        except Exception as e:
            print("Error parsing", pdf_url, e)

if __name__ == "__main__":
    parse_files()
