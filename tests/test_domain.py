import copy
import json
import tempfile
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

    def test_clue_record_covers_required_elements(self):
        record = self.value["clue_record"]
        self.assertTrue(record["content_summary"])
        self.assertTrue(record["attachment_fingerprints"])
        self.assertTrue(record["involved_parties"])
        self.assertTrue(record["product_scope"])
        self.assertIn(record["urgency"], ("一般", "紧急", "特急"))

    def test_events_form_continuous_reasoned_record(self):
        events = self.value["events"]
        self.assertEqual(
            [event["seq"] for event in events], list(range(1, len(events) + 1))
        )
        for event in events:
            self.assertTrue(event["reason"])
        for kind in ("查阅", "转交", "退回"):
            self.assertTrue(any(event["type"] == kind for event in events), kind)

    def test_handler_gets_minimum_necessary_fields(self):
        fields = self.value["identity_policy"]["handler_minimum_fields"]
        self.assertIn("举报内容摘要", fields)
        self.assertNotIn("监督员身份", fields)

    def test_anonymous_channel_shows_nodes_and_responses(self):
        visible = self.value["anonymous_channel"]["visible_to_reporter"]
        self.assertIn("受理节点", visible)
        self.assertIn("结案回应", visible)

    def test_handling_rules_cover_required_situations(self):
        for situation in ("重复举报", "跨区域行为", "监督员离职", "材料撤回", "利益冲突"):
            self.assertIn(situation, self.value["handling_rules"])

    def test_oversight_covers_required_capabilities(self):
        for capability in ("超期发现", "越权访问发现", "打击报复迹象", "身份中立证明"):
            self.assertIn(capability, self.value["oversight"])

    def test_event_without_reason_is_rejected(self):
        broken = copy.deepcopy(self.value)
        broken["events"][0]["reason"] = ""
        self.assertRaises(ValueError, self._reload, broken)

    def test_discontinuous_events_are_rejected(self):
        broken = copy.deepcopy(self.value)
        broken["events"][3]["seq"] = 99
        self.assertRaises(ValueError, self._reload, broken)

    def test_identity_disclosure_without_detail_is_rejected(self):
        broken = copy.deepcopy(self.value)
        broken["events"].append(
            {
                "seq": len(broken["events"]) + 1,
                "type": "身份揭示",
                "actor_role": "价格执法承办人员",
                "reason": "示例：调查必需",
                "at": "2026-08-20T09:00:00+08:00",
            }
        )
        self.assertRaises(ValueError, self._reload, broken)

    @staticmethod
    def _reload(value):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "domain.json"
            path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
            return load_domain(path)


if __name__ == "__main__":
    unittest.main()
