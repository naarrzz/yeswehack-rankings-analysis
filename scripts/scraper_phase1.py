"""
Phase 1: Fetch all-time top-100 rankings from YesWeHack.

Endpoint: GET https://api.yeswehack.com/ranking?page={n}
Discovered via Firefox DevTools -> Network -> XHR filter.

Output: hunters_rankings.csv (100 rows)
"""
import time
import requests
import pandas as pd

RANKING_URL = "https://api.yeswehack.com/ranking"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ywh-research-scraper/1.0 (technical-assessment)",
}


def fetch_rankings() -> pd.DataFrame:
    """Fetch all pages of the all-time rankings and return as a DataFrame."""
    # Fetch first page to determine total number of pages
    r = requests.get(RANKING_URL, params={"page": 1}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    first = r.json()
    total_pages = first["pagination"]["nb_pages"]

    items = list(first["items"])
    for page in range(2, total_pages + 1):
        time.sleep(0.5)  # be polite
        resp = requests.get(RANKING_URL, params={"page": page}, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        items.extend(resp.json()["items"])

    rows = []
    for h in items:
        avatar = h.get("avatar") or {}
        rows.append({
            "rank":              h["rank"],
            "username":          h["username"],
            "slug":              h["slug"],
            "points":            h["points"],
            "is_public":         h["hunter_profile"]["public"],
            "kyc_status":        h["kyc_status"],
            "has_custom_avatar": avatar.get("name") is not None,
        })
    return pd.DataFrame(rows).sort_values("rank").reset_index(drop=True)


if __name__ == "__main__":
    df = fetch_rankings()
    df.to_csv("hunters_rankings.csv", index=False)
    print(f"Saved {len(df)} hunters to hunters_rankings.csv")
