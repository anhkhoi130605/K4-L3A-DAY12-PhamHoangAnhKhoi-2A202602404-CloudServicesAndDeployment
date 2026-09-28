"""CP3 — Cost guard: chặn chi phí trước khi hóa đơn chặn bạn.

Rate limit giới hạn *số lượng* request. Cost guard giới hạn *số tiền*: một
user gửi 10 request/phút nhưng mỗi request 50k token vẫn đốt sạch ngân sách.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status

# Giữ dữ liệu chi tiêu thêm ~40 ngày để còn đối soát sang tháng sau
KEY_TTL_SECONDS = 40 * 24 * 3600


class CostGuard:
    def __init__(self, client, monthly_budget_usd: float) -> None:
        self.client = client
        self.budget = monthly_budget_usd

    @staticmethod
    def current_month() -> str:
        """CHO SẴN — nhãn tháng hiện tại dạng '2026-08' (UTC)."""
        return datetime.now(timezone.utc).strftime("%Y-%m")

    @classmethod
    def _key(cls, user_id: str, month: str | None = None) -> str:
        """CHO SẴN — khóa Redis theo từng user, từng tháng."""
        return f"cost:{user_id}:{month or cls.current_month()}"

    def spent(self, user_id: str, month: str | None = None) -> float:
        """Số tiền user đã tiêu trong tháng.

        TODO (CP3): đọc ``self.client.get(self._key(user_id, month))``.
        Key chưa tồn tại → Redis trả None → hàm này phải trả ``0.0``.
        Nhớ ép kiểu ``float(...)`` vì Redis trả về chuỗi.
        """
        key = self._key(user_id, month)
        value = self.client.get(key)

        if value is None:
            return 0.0

        return float(value)

    def check(
        self,
        user_id: str,
        estimated_cost: float = 0.0,
        month: str | None = None,
    ) -> None:
        """Cho qua nếu còn ngân sách, ngược lại raise 402.

        TODO (CP3): nếu ``spent(user_id) + estimated_cost > self.budget``
        → raise ``HTTPException(status_code=402, detail="monthly budget exceeded")``.
        402 = Payment Required, đúng ngữ nghĩa cho tình huống hết ngân sách.
        """
        if self.spent(user_id, month=month) + estimated_cost > self.budget:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="monthly budget exceeded",
            )

    def record(self, user_id: str, cost: float, month: str | None = None) -> float:
        """Cộng dồn chi phí vừa phát sinh, trả về tổng mới.

        TODO (CP3):
          1. ``total = self.client.incrbyfloat(key, cost)``
          2. ``self.client.expire(key, KEY_TTL_SECONDS)``
          3. ``return float(total)``
        """
        key = self._key(user_id, month)
        total = self.client.incrbyfloat(key, cost)
        self.client.expire(key, KEY_TTL_SECONDS)
        return float(total)
