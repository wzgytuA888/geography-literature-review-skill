from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from geo_review.clients.openalex import abstract_from_index
from geo_review.clients.crossref import CrossrefClient
from geo_review.export import export_review
from geo_review.http import ResilientClient
from geo_review.models import PaperRecord, SearchLogEntry, normalize_doi, normalize_title
from geo_review.pipeline import apply_screening, build_queries, deduplicate, score_relevance


class FakeResponse:
    def __init__(self, status: int, payload: dict):
        self.status_code = status
        self._payload = payload
        self.headers = {}

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(str(self.status_code))

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = 0

    def request(self, *args, **kwargs):
        self.calls += 1
        return FakeResponse(200, {"value": 42})


class V2PipelineTests(unittest.TestCase):
    def test_identifier_normalization(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1000/ABC."), "10.1000/abc")
        self.assertEqual(normalize_title("  Climate—Change: A Test! "), "climate change a test")

    def test_query_builder_is_bounded_and_reproducible(self):
        queries = build_queries("Permafrost and vegetation",
                                ["permafrost degradation", "NDVI", "Tibetan Plateau"],
                                max_queries=4)
        self.assertEqual(queries[0], "Permafrost and vegetation")
        self.assertLessEqual(len(queries), 4)
        self.assertEqual(queries, build_queries("Permafrost and vegetation",
                                                ["permafrost degradation", "NDVI", "Tibetan Plateau"],
                                                max_queries=4))

    def test_dedup_priority_and_uncertain_flag(self):
        records = [
            PaperRecord(title="A climate study", doi="10.1/ABC", source_database=["A"]),
            PaperRecord(title="A climate study revised", doi="https://doi.org/10.1/abc",
                        semantic_scholar_id="S2", source_database=["B"]),
            PaperRecord(title="Vegetation response across Tibetan Plateau"),
            PaperRecord(title="Vegetation responses across the Tibetan Plateau"),
        ]
        unique, log = deduplicate(records)
        self.assertEqual(len(unique), 3)
        self.assertEqual(unique[0].source_database, ["A", "B"])
        self.assertTrue(any(row["action"] == "merged" and row["reason"] == "doi" for row in log))
        self.assertTrue(unique[-1].possible_duplicate)

    def test_openalex_abstract_reconstruction(self):
        self.assertEqual(abstract_from_index({"world": [1], "hello": [0]}), "hello world")

    def test_cache_prevents_second_request(self):
        with tempfile.TemporaryDirectory() as td:
            session = FakeSession()
            root = Path(td)
            client = ResilientClient("mock", root / "cache", root / "errors.log",
                                     min_interval=0, session=session)
            self.assertEqual(client.request_json("GET", "https://example.test", params={"q": "x"}),
                             {"value": 42})
            self.assertEqual(client.request_json("GET", "https://example.test", params={"q": "x"}),
                             {"value": 42})
            self.assertEqual(session.calls, 1)

    def test_relevance_formula_disclosed(self):
        rows = [PaperRecord(title="Permafrost vegetation response", year=2025,
                            citation_count=10, abstract="Tibetan Plateau", doi="10.1/x")]
        score_relevance(rows, "permafrost vegetation Tibetan Plateau", 2026)
        self.assertGreater(rows[0].relevance_score, 0)
        self.assertIn("triage only", rows[0].relevance_score_method)

    def test_crossref_publication_metadata(self):
        row = CrossrefClient._normalize({
            "title": ["Test"], "container-title": ["Journal"], "DOI": "10.1/Z",
            "publisher": "Publisher", "volume": "4", "issue": "2",
            "published": {"date-parts": [[2025, 3, 4]]}}, "10.1/z")
        self.assertEqual(row.publication_date, "2025-3-4")
        self.assertEqual(row.publisher, "Publisher")

    def test_explicit_screening(self):
        rows = [PaperRecord(paper_id="P0001", title="Test")]
        apply_screening(rows, {"P0001": {"include": False, "exclude_reason": "wrong_topic"}})
        self.assertFalse(rows[0].include)
        self.assertEqual(rows[0].screening_status, "excluded")

    def test_structured_exports(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            paths = export_review(out, [PaperRecord(paper_id="P0001", title="Test")],
                                  [SearchLogEntry("Semantic Scholar", "test", {}, None, 1)])
            self.assertTrue(Path(paths["json"]).exists())
            self.assertTrue(Path(paths["csv"]).exists())
            self.assertTrue(Path(paths["xlsx"]).exists())
            data = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
            self.assertIsNone(data[0]["study_area"])


if __name__ == "__main__":
    unittest.main()
