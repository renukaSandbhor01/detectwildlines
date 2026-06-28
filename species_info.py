"""
species_info.py — Looks up real-world information about a predicted species.

Uses Wikipedia's public REST API (no API key, no signup needed).
Two steps:
  1. Search for the closest matching Wikipedia article title for the
     model's label (e.g. "Cock" -> "Rooster"), since ImageNet labels
     don't always exactly match an article title.
  2. Fetch a short summary + link for that article.
"""

import requests

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"


def get_species_info(label):
    """
    Returns a dict: {"title": ..., "extract": ..., "url": ...}
    or None if nothing could be found (e.g. no internet connection).
    """
    title = _find_best_wiki_title(label)
    if not title:
        return None

    try:
        response = requests.get(WIKI_SUMMARY_URL.format(title), timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", label),
                "extract": data.get("extract", "No description available."),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "#"),
            }
    except requests.RequestException:
        # No internet, timeout, or Wikipedia unreachable — fail quietly,
        # the app should still show the prediction even without field notes.
        pass

    return None


def _find_best_wiki_title(query):
    """
    Wikipedia's 'opensearch' endpoint takes any text and returns the
    closest matching article titles — this bridges the gap between a
    raw ImageNet label and a real encyclopedia entry.
    """
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 1,
        "namespace": 0,
        "format": "json",
    }
    try:
        response = requests.get(WIKI_SEARCH_URL, params=params, timeout=5)
        if response.status_code == 200:
            results = response.json()
            matching_titles = results[1]
            if matching_titles:
                return matching_titles[0]
    except requests.RequestException:
        pass

    return query  # fall back to trying the raw label directly
