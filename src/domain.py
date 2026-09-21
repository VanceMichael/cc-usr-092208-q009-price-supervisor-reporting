"""读取并检查共享的领域资料。"""

import json
from pathlib import Path

REQUIRED_FIELDS = {
    "domain",
    "version",
    "sample_id",
    "actors",
    "facts",
    "constraints",
    "clue_record",
    "events",
    "identity_policy",
    "anonymous_channel",
    "handling_rules",
    "oversight",
}

CLUE_FIELDS = {
    "report_id",
    "channel",
    "reporter_alias",
    "content_summary",
    "attachment_fingerprints",
    "involved_parties",
    "product_scope",
    "urgency",
    "status",
}

POLICY_FIELDS = {"default_visibility", "disclosure_conditions", "handler_minimum_fields"}

REQUIRED_RULES = {"重复举报", "跨区域行为", "监督员离职", "材料撤回", "利益冲突"}

REQUIRED_OVERSIGHT = {"超期发现", "越权访问发现", "打击报复迹象", "身份中立证明"}


def load_domain(path: Path) -> dict:
    """返回字段完整且带版本的业务资料。"""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not REQUIRED_FIELDS.issubset(value):
        raise ValueError("共享资料缺少必要字段")
    if (
        value["version"] < 2
        or len(value["actors"]) < 2
        or len(value["facts"]) < 2
        or len(value["constraints"]) < 2
    ):
        raise ValueError("共享资料内容不完整")
    _check_clue_record(value["clue_record"])
    _check_events(value["events"], set(value["actors"]))
    if not POLICY_FIELDS.issubset(value["identity_policy"]):
        raise ValueError("身份揭示规则不完整")
    if not REQUIRED_RULES.issubset(value["handling_rules"]):
        raise ValueError("处理规则缺少必备情形")
    if not REQUIRED_OVERSIGHT.issubset(value["oversight"]):
        raise ValueError("监察能力不完整")
    return value


def _check_clue_record(record: dict) -> None:
    """线索记录须覆盖举报内容、附件指纹、涉及主体、商品范围与紧急程度。"""
    if not CLUE_FIELDS.issubset(record):
        raise ValueError("线索记录缺少必要字段")
    if not record["attachment_fingerprints"]:
        raise ValueError("附件指纹不能为空")


def _check_events(events: list, actors: set) -> None:
    """事件记录须连续，操作人须为已知参与方，且每次操作都留下理由。"""
    if not events:
        raise ValueError("事件记录不能为空")
    for position, event in enumerate(events, start=1):
        if event.get("seq") != position:
            raise ValueError("事件序号必须连续")
        if event.get("actor_role") not in actors:
            raise ValueError("事件操作人须为已知参与方")
        if not event.get("reason"):
            raise ValueError("任何查阅、转交或退回都要留下理由")
        if event.get("type") == "身份揭示" and not event.get("detail"):
            raise ValueError("身份揭示必须记录必要范围与审批")
