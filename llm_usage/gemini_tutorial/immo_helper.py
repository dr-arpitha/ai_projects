"""
Scrape Immoweb search results for apartments for sale in Etterbeek (1040) up to €300,000.

Target URL (example):
https://www.immoweb.be/en/search/apartment/for-sale/etterbeek/1040?countries=BE&maxPrice=300000&page=1&orderBy=relevance

What it does
- Navigates every results page starting from the given URL
- Extracts: listing_id, title, price_eur, locality, zipcode, bedrooms, bathrooms,
  habitable_area_sqm, floor, epc, property_type, url, agency, date_scraped
- Saves to CSV (immoweb_etterbeek_300k.csv) and JSON

Notes
- Uses Playwright (Chromium) to render JS (Immoweb is heavily client-side).
- Be respectful: default delay and per-page throttling included.
- Inspectors change: selectors are written to be resilient but may need tweaks over time.
- Legal/ToS: make sure scraping is allowed for your use. Add robots.txt checks and rate limits as needed.

Setup
  pip install playwright pandas
  playwright install chromium

Run
  python immoweb_scraper.py --start-url "<paste the url>" --max-pages 10 --out csv json
"""

from __future__ import annotations
import asyncio
import json
import math
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import pandas as pd
from playwright.async_api import async_playwright

LISTING_CARD_SEL = "[data-item='result'] , article:has(a[href*='/en/classified'])"
NEXT_BUTTON_SEL = "a[aria-label*='Next'], a[rel='next']"
PRICE_SEL = "[data-qa='card-price'], [class*='price']"
TITLE_SEL = "[data-qa='card-title'], h2, h3"
META_SEL = "[data-qa='card-parameters'], ul, .classified__information--property, [class*='property-parameters']"
AGENCY_SEL = "[data-qa='card-agency'], [class*='agency']"

@dataclass
class Listing:
    listing_id: Optional[str]
    title: Optional[str]
    price_eur: Optional[float]
    locality: Optional[str]
    zipcode: Optional[str]
    bedrooms: Optional[float]
    bathrooms: Optional[float]
    habitable_area_sqm: Optional[float]
    floor: Optional[str]
    epc: Optional[str]
    property_type: Optional[str]
    url: Optional[str]
    agency: Optional[str]
    date_scraped: str

    @staticmethod
    def parse_float(text: str) -> Optional[float]:
        if not text:
            return None
        # Keep digits, dot and comma, then normalize comma to dot
        s = re.sub(r"[^0-9,\.]", "", text)
        s = s.replace(".", "").replace(",", ".") if s.count(",") == 1 and s.count(".") > 1 else s.replace(",", "")
        try:
            return float(s)
        except:
            return None


def parse_meta_block(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    t = re.sub(r"\s+", " ", text or "").strip().lower()
    # Bedrooms/bathrooms
    m = re.search(r"(\d+[\.,]?\d*)\s*(bed|bedroom|chambre|slaapkamer)s?", t)
    if m:
        out["bedrooms"] = Listing.parse_float(m.group(1))
    m = re.search(r"(\d+[\.,]?\d*)\s*(bath|bathroom|salle de bain|badkamer)s?", t)
    if m:
        out["bathrooms"] = Listing.parse_float(m.group(1))
    # Area
    m = re.search(r"(\d+[\.,]?\d*)\s*(m²|sqm|m2)", t)
    if m:
        out["habitable_area_sqm"] = Listing.parse_float(m.group(1))
    # Floor
    m = re.search(r"(ground|rez|rdc|first|1st|2nd|3rd|\d+e?)\s*(floor|étage|verdieping)", t)
    if m:
        out["floor"] = m.group(0)
    # EPC / energy
    m = re.search(r"epc\s*[:\-]?\s*([a-g][+\-]?)", t)
    if m:
        out["epc"] = m.group(1).upper()
    return out

async def extract_card(card) -> Listing:
    # URL
    url = None
    link = await card.query_selector("a[href*='/en/classified'] , a[href*='/fr/annonce'] , a[href*='/nl/zoekertje']")
    if link:
        url = await link.get_attribute("href")
    # Title
    title = None
    for sel in TITLE_SEL.split(','):
        el = await card.query_selector(sel.strip())
        if el:
            title = (await el.inner_text()).strip()
            break
    # Price
    price_eur = None
    for sel in PRICE_SEL.split(','):
        el = await card.query_selector(sel.strip())
        if el:
            price_text = (await el.inner_text()).strip()
            m = re.search(r"([\d\.,\s]+)", price_text)
            if m:
                price_eur = Listing.parse_float(m.group(1))
            break
    # Agency
    agency = None
    for sel in AGENCY_SEL.split(','):
        el = await card.query_selector(sel.strip())
        if el:
            agency = (await el.inner_text()).strip()
            break
    # Meta block
    meta_text = None
    for sel in META_SEL.split(','):
        el = await card.query_selector(sel.strip())
        if el:
            meta_text = (await el.inner_text()).strip()
            if meta_text:
                break
    meta = parse_meta_block(meta_text or "")

    # Try to guess locality/zipcode from anchors or small text
    locality = None
    zipcode = None
    small = await card.query_selector("a[href*='/en/'], a[href*='/fr/'], a[href*='/nl/'], small, span")
    if small:
        s = (await small.inner_text()).strip()
        m = re.search(r"(\d{4})\s+([\w\-\'\s]+)", s)
        if m:
            zipcode = m.group(1)
            locality = m.group(2).strip()

    # Listing id from URL
    listing_id = None
    if url:
        m = re.search(r"/(\d{6,})", url)
        if m:
            listing_id = m.group(1)

    return Listing(
        listing_id=listing_id,
        title=title,
        price_eur=price_eur,
        locality=locality,
        zipcode=zipcode,
        bedrooms=meta.get("bedrooms"),
        bathrooms=meta.get("bathrooms"),
        habitable_area_sqm=meta.get("habitable_area_sqm"),
        floor=meta.get("floor"),
        epc=meta.get("epc"),
        property_type="apartment",
        url=url,
        agency=agency,
        date_scraped=datetime.now(timezone.utc).isoformat(),
    )

async def scrape(start_url: str, max_pages: int = 50, throttle_ms: int = 1500) -> List[Listing]:
    results: List[Listing] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        url = start_url
        for page_idx in range(max_pages):
            await page.goto(url, wait_until="load")
            await page.wait_for_timeout(throttle_ms)

            # accept cookies if present
            try:
                btn = await page.query_selector("button:has-text('Accept'), button:has-text('Accepter'), button:has-text('Accepteren')")
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(500)
            except:
                pass

            cards = await page.query_selector_all(LISTING_CARD_SEL)
            if not cards:
                # Try to wait for network idle then retry once
                await page.wait_for_load_state("networkidle")
                cards = await page.query_selector_all(LISTING_CARD_SEL)

            for card in cards:
                try:
                    results.append(await extract_card(card))
                except Exception:
                    continue

            # Find next page link
            next_href = None
            next_btn = await page.query_selector(NEXT_BUTTON_SEL)
            if next_btn:
                next_href = await next_btn.get_attribute("href")
            if not next_href:
                # Build next url by incrementing &page=
                m = re.search(r"[?&]page=(\d+)", url)
                if m:
                    n = int(m.group(1)) + 1
                    url = re.sub(r"([?&]page=)\d+", f"\\g<1>{n}", url)
                else:
                    sep = '&' if '?' in url else '?'
                    url = f"{url}{sep}page=2"
            else:
                if next_href.startswith("http"):
                    url = next_href
                else:
                    from urllib.parse import urljoin
                    url = urljoin(page.url, next_href)

            # Stop if no new cards found or pagination didn't move
            if not next_href and "page=" in url and page_idx > 0 and len(cards) == 0:
                break

        await browser.close()
    return results


def to_dataframe(items: List[Listing]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(it) for it in items])
    # de-dup by listing_id/url
    if not df.empty:
        df = df.drop_duplicates(subset=[c for c in ["listing_id", "url"] if c in df.columns])
        df = df.sort_values(by=["price_eur", "habitable_area_sqm"], ascending=[True, False], na_position='last')
    return df

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-url", required=True)
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--out", nargs="+", choices=["csv", "json"], default=["csv"]) 
    args = ap.parse_args()

    items = asyncio.run(scrape(args.start_url, args.max_pages))
    df = to_dataframe(items)

    if "csv" in args.out:
        df.to_csv("immoweb_etterbeek_300k.csv", index=False)
        print("Saved CSV -> immoweb_etterbeek_300k.csv")
    if "json" in args.out:
        with open("immoweb_etterbeek_300k.json", "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        print("Saved JSON -> immoweb_etterbeek_300k.json")

    print(f"Rows: {len(df)}")

