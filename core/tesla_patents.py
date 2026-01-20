from __future__ import annotations
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import requests

DEFAULT_TIMEOUT = 18

@dataclass(frozen=True)
class TeslaPatent:
    idx: int
    title: str
    filing_date: str
    application_number: str
    grant_date: str
    patent_number: str

def load_dataset(path: str) -> Dict[str, Any]:
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_one(path: str, seed: Optional[int] = None) -> TeslaPatent:
    data = load_dataset(path)
    items = data.get("items") or []
    if not items:
        raise ValueError("Tesla patent dataset is empty.")
    rng = random.Random(seed) if seed is not None else random
    row = rng.choice(items)
    return TeslaPatent(
        idx=int(row["idx"]),
        title=str(row["title"]),
        filing_date=str(row["filing_date"]),
        application_number=str(row.get("application_number") or ""),
        grant_date=str(row["grant_date"]),
        patent_number=str(row["patent_number"]),
    )

def museum_source_url() -> str:
    # Official museum document used for the index list
    return "https://tesla-museum.org/wp-content/uploads/2023/05/lista_patenata_eng.pdf"

def uspto_pdf_urls(patent_number: str) -> List[str]:
    # We provide a small set of official-looking PDF endpoints.
    # The bot will try each in order and use the first that responds with a PDF.
    pn = patent_number.strip().lstrip("0")
    return [
        # USPTO Patent Public Search / image-ppubs PDF endpoint (commonly used for downloads)
        f"https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/{pn}",
        # Alternative older endpoint patterns may vary; kept minimal.
    ]

def try_download_pdf(patent_number: str, dest_path: str) -> Tuple[bool, str]:
    urls = uspto_pdf_urls(patent_number)
    ua = os.getenv("TESLA_USER_AGENT") or "AcademicDiscordBot/1.0 (contact: set TESLA_USER_AGENT)"
    for url in urls:
        try:
            r = requests.get(url, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": ua})
            if r.status_code == 200 and ("application/pdf" in (r.headers.get("content-type") or "")):
                with open(dest_path, "wb") as f:
                    f.write(r.content)
                return True, url
        except Exception:
            continue
    return False, urls[0] if urls else ""
