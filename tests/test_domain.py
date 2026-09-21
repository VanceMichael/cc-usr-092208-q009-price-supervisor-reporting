import unittest
from pathlib import Path
from src.domain import load_domain

class DomainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = load_domain(Path("fixtures/domain.json"))

    def test_fixture_matches_domain(self):
        self.assertEqual(self.value["domain"], "price-supervisor-reporting")
        self.assertGreaterEqual(len(self.value["constraints"]), 2)

    def test_clue_record_tracks_required_elements(self):
        record = self.value["clue_record"]
        self.assertTrue(record["attachment_fingerprints"])
        self.assertTrue(all(fp["algorithm"] == "sha256" for fp in record["attachment_fingerprints"]))
        self.assertTrue(record["involved_subjects"])
        self.assertTrue(record["product_scope"])
        self.assertIn(record["urgency"], {"一般", "紧急", "特急"})

    def test_every_event_has_reason_and_continuous_seq(self):
        events = self.value["lifecycle_events"]
        self.assertTrue(all(event["reason"] for event in events))
        self.assertEqual([event["seq"] for event in events], list(range(1, len(events) + 1)))

    def test_handling_rules_cover_five_situations(self):
        rules = self.value["handling_rules"]
        for key in ("duplicate_reports", "cross_region", "supervisor_departure",
                    "withdrawal", "conflict_of_interest"):
            self.assertTrue(rules[key])

    def test_identity_protection_and_oversight(self):
        protection = self.value["identity_protection"]
        self.assertTrue(protection["pseudonym"])
        self.assertTrue(protection["disclosure_scope"])
        self.assertTrue(protection["anonymous_channel"])
        oversight = self.value["oversight"]
        for key in ("overdue_watch", "access_audit", "retaliation_watch", "integrity_check"):
            self.assertTrue(oversight[key])

if __name__ == "__main__":
    unittest.main()
