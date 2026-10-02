"""Fetch patent records through the cache. Source order: cache, then Google Patents.

EPO OPS and USPTO PPUBS fallbacks plug in here later (PLAN.md §9.1 D).
Google Patents always returns the whole page, so every fresh fetch is stored at level 'full'.
"""

import asyncio

from ideacheck.cache import Cache, Throttled
from ideacheck.numbers import canonical, google_forms

GOOGLE = "google_patents"
GOOGLE_MIN_INTERVAL = 25.0   # seconds between calls, shared across processes
GOOGLE_COOLDOWN = 15 * 60    # back-off after a 503 or a hang; Phase 0 blocks lasted 40-60+ min
GOOGLE_TIMEOUT = 120.0


def google_record(p) -> dict:
    """Flatten a patent_client_agents Google Patents record into a plain dict."""
    return {
        "title": p.title, "abstract": p.abstract, "family_id": p.family_id,
        "kind_code": p.kind_code, "priority_date": str(p.priority_date),
        "filing_date": str(p.filing_date), "publication_date": str(p.publication_date),
        "status": p.status, "legal_status": p.legal_status_category,
        "expiration_date": str(p.expiration_date),
        "assignee": p.current_assignee or p.original_assignee, "inventors": p.inventors,
        "source_language": p.source_language,
        "cpc": [c.code for c in (p.cpc_classifications or [])],
        "claims": p.claims, "structured_limitations": p.structured_limitations,
        "description": p.description_markdown or p.description,
    }


async def _fetch_google(number: str, cache: Cache) -> dict:
    from patent_client_agents.google_patents import GooglePatentsClient

    last_error: Exception | None = None
    async with GooglePatentsClient() as client:
        for form in google_forms(number):
            cache.wait_turn(GOOGLE, GOOGLE_MIN_INTERVAL)
            try:
                return google_record(await asyncio.wait_for(client.get_patent_data(form),
                                                             GOOGLE_TIMEOUT))
            except asyncio.TimeoutError as e:  # the client retries 503s internally; a hang means throttling
                cache.mark_throttled(GOOGLE, GOOGLE_COOLDOWN)
                raise Throttled(GOOGLE, GOOGLE_COOLDOWN) from e
            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    cache.mark_throttled(GOOGLE, GOOGLE_COOLDOWN)
                    raise Throttled(GOOGLE, GOOGLE_COOLDOWN) from e
                last_error = e  # wrong number form: try the next one
    raise LookupError(f"{canonical(number)} not found on Google Patents: {last_error}")


def get_record(number: str, level: str = "details", cache: Cache | None = None,
               allow_remote: bool = True) -> dict:
    """Return a record from the cache, fetching it remotely on a miss.

    Raises Throttled when the remote source is cooling down, and LookupError
    when the number is unknown or remote access is disabled.
    """
    cache = cache or Cache()
    hit = cache.get(number, level)
    if hit is not None:
        return hit
    if not allow_remote:
        raise LookupError(f"{canonical(number)} not cached and remote access is disabled")
    record = asyncio.run(_fetch_google(number, cache))
    cache.put(number, GOOGLE, "full", record)
    return record
