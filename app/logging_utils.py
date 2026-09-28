"""CP1 — Structured logging.

`print("user abc hỏi gì đó")` là log cho người đọc. Cloud (Railway, Render,
Cloud Run, Datadog...) đọc log bằng máy: một dòng = một JSON object thì mới
lọc/đếm/cảnh báo được. Đây là khác biệt lớn giữa localhost và production.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """CHO SẴN — thời điểm hiện tại theo ISO-8601, múi giờ UTC."""
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, level: str = "info", **fields) -> str:
    """Ghi một dòng log JSON ra stdout.

    TODO (CP1): tạo dict gồm tối thiểu 3 khóa
        - "event"     : tên sự kiện, lấy từ tham số ``event``
        - "level"     : mức log, VIẾT THƯỜNG (dùng ``level.lower()``)
        - "timestamp" : ``utc_now_iso()``
    rồi gộp thêm mọi cặp key/value trong ``**fields``.

    In chuỗi JSON đó ra stdout **trên một dòng duy nhất**
    (``json.dumps(..., ensure_ascii=False)``, đừng dùng ``indent``) và
    trả về chính chuỗi đó.

    Ví dụ:
        >>> log_event("ask_completed", user_id="sv01", cost_usd=0.0001)
        '{"event": "ask_completed", "level": "info", "timestamp": "...", ...}'
    """

    payload = {
        "event": event,   #system and user log
        "level": level.lower(), #info, warn, error, debug
        "timestamp": utc_now_iso(),
        **fields,
    }

    log_line = json.dumps(payload, ensure_ascii=False)
    print(log_line, file=sys.stdout)
    return log_line
