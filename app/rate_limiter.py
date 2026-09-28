"""CP3 — Rate limiting bằng thuật toán sliding window.

Đếm số request trong 60 giây **gần nhất** (cửa sổ trượt), thay vì đếm theo
phút đồng hồ. Đếm theo phút đồng hồ có lỗ hổng: 10 request lúc 10:00:59 và
10 request lúc 10:01:01 = 20 request trong 2 giây mà vẫn "đúng luật".

Cấu trúc dữ liệu: Redis Sorted Set (ZSET), score = timestamp của request.
"""

from __future__ import annotations

import time
import uuid

from fastapi import HTTPException, status

WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(self, client, limit_per_minute: int) -> None:
        self.client = client
        self.limit = limit_per_minute

    @staticmethod
    def _key(user_id: str) -> str:
        """CHO SẴN — mỗi user một key riêng."""
        return f"ratelimit:{user_id}"

    def hit_count(self, user_id: str, now: float | None = None) -> int:
        """Số request của user trong ``WINDOW_SECONDS`` giây gần nhất.

        TODO (CP3):
          1. ``now = now if now is not None else time.time()``
          2. Xóa các entry cũ hơn cửa sổ:
             ``self.client.zremrangebyscore(key, 0, now - WINDOW_SECONDS)``
          3. Trả về ``self.client.zcard(key)``
        """

        now = now if now is not None else time.time()
        key = self._key(user_id)

        # Xóa toàn bộ phần tử có timestamp nằm ngoài cửa sổ [now - WINDOW_SECONDS, now]
        self.client.zremrangebyscore(key, 0, now - WINDOW_SECONDS)

        # Đếm số lượng phần tử còn lại trong Sorted Set
        return int(self.client.zcard(key))

    def check(self, user_id: str, now: float | None = None) -> None:
        """Cho qua nếu còn quota, ngược lại raise 429.

        TODO (CP3):
          1. ``now = now if now is not None else time.time()``
          2. Gọi ``self.hit_count(user_id, now)``.
          3. Nếu số đó ``>= self.limit`` → raise
             ``HTTPException(status_code=429, detail="rate limit exceeded",
                             headers={"Retry-After": str(WINDOW_SECONDS)})``
          4. Chưa vượt → ghi nhận request này:
             ``self.client.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})``
             (member phải là chuỗi DUY NHẤT, nếu không hai request cùng
             timestamp sẽ ghi đè nhau và bạn đếm thiếu)
             rồi ``self.client.expire(key, WINDOW_SECONDS)`` để key tự dọn.

        Lưu ý thứ tự: **kiểm tra trước, ghi nhận sau**. Ghi trước rồi mới đếm
        sẽ chặn nhầm ngay ở request thứ ``limit``.
        """
        now = now if now is not None else time.time()
        key = self._key(user_id)

        # 1. Đếm số request hiện có trong cửa sổ 60s
        current_hits = self.hit_count(user_id, now)

        # 2. Chặn nếu đã đạt hoặc vượt ngưỡng giới hạn
        if current_hits >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        # 3. Ghi nhận request mới với member duy nhất (timestamp + uuid) và score là timestamp
        member_id = f"{now}:{uuid.uuid4().hex}"
        self.client.zadd(key, {member_id: now})

        # 4. Đặt TTL cho key bằng độ dài cửa sổ để Redis tự giải phóng RAM
        self.client.expire(key, WINDOW_SECONDS)
