# scraper/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class DocumentMeta:
    id: Optional[int]
    title: str
    url: str
    date_published: Optional[datetime]
    summary: Optional[str]
    category: Optional[str]
    hash: str
    created_at: Optional[datetime] = None
    file_links: List[str] = None
