"""
Tests for Posting Verification Pass.
Covers: live vs filled posting detection, queue sorting by verification status.
"""

from unittest.mock import patch
from audit_and_purge_404_urls import verify_posting, verify_active_postings

class MockHttpResponse:
    def __init__(self, content: bytes, code: int = 200):
        self._content = content
        self._code = code
    def getcode(self):
        return self._code
    def read(self):
        return self._content
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def test_verify_posting_active_vs_stale():
    live_html = b"<html><body><h1>Director of Technology</h1><button>Apply</button></body></html>"
    stale_html = b"<html><body><h1>Job Expired</h1><p>This position has been filled</p></body></html>"

    def mock_urlopen(req, timeout=6):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "live" in url:
            return MockHttpResponse(live_html, 200)
        return MockHttpResponse(stale_html, 200)

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        status_live, _ = verify_posting("https://example.com/live")
        status_stale, _ = verify_posting("https://example.com/stale")

        assert status_live == "verified"
        assert status_stale == "unconfirmed"

def test_verify_active_postings_sorts_queue():
    state = {
        "review_queue": [
            {"company": "FilledCorp", "title": "Director", "url": "https://example.com/stale", "match_score": 95},
            {"company": "ActiveCorp", "title": "Director", "url": "https://example.com/live", "match_score": 85}
        ]
    }

    def mock_urlopen(req, timeout=6):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "live" in url:
            return MockHttpResponse(b"<html>Apply Now</html>", 200)
        return MockHttpResponse(b"<html>This job has expired</html>", 200)

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        res_state = verify_active_postings(state)
        q = res_state["review_queue"]

        assert q[0]["company"] == "ActiveCorp"
        assert q[0]["verification"] == "verified"
        assert q[1]["company"] == "FilledCorp"
        assert q[1]["verification"] == "unconfirmed"
