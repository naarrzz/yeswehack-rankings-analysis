"""
Phase 2: Enrich each hunter with profile-page data.

Endpoint: GET https://api.yeswehack.com/hunters/{slug}
Handles 404 (private profile) and 429 (rate limit) gracefully.

Input:  hunters_rankings.csv (from scraper_phase1.py)
Output: hunters_full.csv (100 rows, ~56 with profile fields populated)
"""
import time
import requests
import pandas as pd

PROFILE_URL = "https://api.yeswehack.com/hunters/{slug}"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ywh-research-scraper/1.0 (technical-assessment)",
}
BASE_DELAY  = 1.5   # seconds between requests
RETRY_WAIT  = 65    # seconds to wait after a 429 (if no Retry-After header)
MAX_RETRIES = 3


def fetch_profile(slug: str) -> dict:
    """Fetch a single hunter's profile, gracefully handling 404 and 429."""
    empty = {
        "nationality": None,
        "nb_reports":  None,
        "impact":      None,
        "joined_on":   None,
        "has_twitter": False,
        "has_website": False,
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(PROFILE_URL.format(slug=slug), headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                # Private profile -- expected, not an error
                return empty
            if resp.status_code == 429:
                # Rate-limited -- respect Retry-After header if present
                wait = int(resp.headers.get("Retry-After", RETRY_WAIT))
                print(f"  429 on {slug}, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            p = resp.json()
            return {
                "nationality": p.get("nationality"),
                "nb_reports":  p.get("nb_reports"),
                "impact":      float(p["impact"]) if p.get("impact") else None,
                "joined_on":   p.get("joined_on"),
                "has_twitter": bool(p.get("twitter")),
                "has_website": bool(p.get("website_url")),
            }
        except Exception as e:
            print(f"  WARN {slug}: {e}")
            time.sleep(BASE_DELAY * 2)
    return empty


if __name__ == "__main__":
    df = pd.read_csv("hunters_rankings.csv")
    enrichments = []
    for i, row in df.iterrows():
        if i > 0:
            time.sleep(BASE_DELAY)
        enrichments.append(fetch_profile(row["slug"]))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(df)}")

    df_full = pd.concat([df, pd.DataFrame(enrichments)], axis=1)
    df_full.to_csv("hunters_full.csv", index=False)
    retrieved = df_full["nationality"].notna().sum()
    print(f"Saved hunters_full.csv -- {retrieved} profiles retrieved")
