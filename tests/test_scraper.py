# tests/test_scraper.py
from scraper.crawl import parse_listing, parse_detail

def test_parse_listing_basic():
    html = '<html><body><a href="/node/1">Item</a><a href="/file.pdf">PDF</a></body></html>'
    links = parse_listing(html, "https://mospi.gov.in/")
    assert any("node/1" in l for l in links)

def test_parse_detail_title():
    html = '<html><head><title>My Title</title></head><body><h1>Header</h1></body></html>'
    doc = parse_detail(html, "https://mospi.gov.in/node/1")
    assert "Header" in doc.title or "My Title" in doc.title
