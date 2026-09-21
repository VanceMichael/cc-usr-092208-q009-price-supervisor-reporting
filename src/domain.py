"""读取并检查共享的领域资料。"""

import json
from pathlib import Path

REQUIRED_FIELDS = {
    "domain", "version", "sample_id", "actors", "facts", "constraints",
    "clue_record", "lifecycle_events", "identity_protection", "handling_rules", "oversight",
}

EVENT_TYPES = {
    "受理", "查阅", "身份揭示", "管辖移送", "转交", "退回",
    "补证请求", "补证接收", "并案", "撤回登记", "回避改派", "办结反馈",
}

RULE_KEYS = {
    "duplicate_reports", "cross_region", "supervisor_departure",
    "withdrawal", "conflict_of_interest",
}
OVERSIGHT_KEYS = {"overdue_watch", "access_audit", "retaliation_watch", "integrity_check"}


def load_domain(path: Path) -> dict:
    """返回字段完整且带版本的业务资料。"""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not REQUIRED_FIELDS.issubset(value):
        raise ValueError("共享资料缺少必要字段")
    if value["version"] < 2 or len(value["actors"]) < 2 or len(value["facts"]) < 2 or len(value["constraints"]) < 2:
        raise ValueError("共享资料内容不完整")
    record = value["clue_record"]
    if not record.get("attachment_fingerprints") or not record.get("involved_subjects"):
        raise ValueError("线索记录缺少附件指纹或涉及主体")
    events = value["lifecycle_events"]
    if not events:
        raise ValueError("生命周期事件不能为空")
    for event in events:
        if event.get("type") not in EVENT_TYPES or not event.get("reason"):
            raise ValueError("生命周期事件类型不明或缺少理由")
    if [event["seq"] for event in events] != list(range(1, len(events) + 1)):
        raise ValueError("生命周期事件序号必须连续")
    if not RULE_KEYS.issubset(value["handling_rules"]):
        raise ValueError("处理规则不完整")
    if not OVERSIGHT_KEYS.issubset(value["oversight"]):
        raise ValueError("监察要点不完整")
    return value
