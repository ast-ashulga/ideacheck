import threading
import time

import pytest

from ideacheck.cache import Cache, Throttled
from ideacheck.numbers import canonical, google_forms


def test_number_forms_round_trip():
    assert canonical("US20190183707A1") == "US-2019183707-A1"
    assert canonical("us-2019183707-a1") == "US-2019183707-A1"
    assert canonical("JP4616127B2") == "JP-4616127-B2"
    assert google_forms("US-2019183707-A1") == ["US2019183707A1", "US20190183707A1"]
    assert google_forms("EP-2897566-B1") == ["EP2897566B1"]


def test_full_satisfies_details_but_not_reverse(tmp_path):
    c = Cache(tmp_path / "c.sqlite")
    c.put("JP4616127B2", "google_patents", "details", {"title": "partial"})
    assert c.get("JP-4616127-B2", "details")["title"] == "partial"
    assert c.get("JP-4616127-B2", "full") is None
    c.put("JP-4616127-B2", "google_patents", "full", {"title": "complete"})
    assert c.get("JP-4616127-B2", "details")["title"] == "complete"
    assert c.stats() == {"google_patents/details": 1, "google_patents/full": 1}


def test_rate_governor_spaces_calls_across_threads(tmp_path):
    c = Cache(tmp_path / "c.sqlite")
    stamps = []

    def call():
        c.wait_turn("src", 0.3)
        stamps.append(time.time())

    threads = [threading.Thread(target=call) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stamps.sort()
    assert all(b - a >= 0.28 for a, b in zip(stamps, stamps[1:]))


def test_throttle_blocks_every_caller(tmp_path):
    c = Cache(tmp_path / "c.sqlite")
    c.mark_throttled("src", 60)
    with pytest.raises(Throttled):
        Cache(tmp_path / "c.sqlite").wait_turn("src", 0)
