"""CP1 — Cấu hình theo 12-Factor.

Nguyên tắc: **không có giá trị cấu hình nào nằm trong code**. Tất cả đến từ
biến môi trường, để cùng một image chạy được ở laptop, staging và production
mà không phải sửa một dòng code nào.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toàn bộ cấu hình của service.

    TODO (CP1): khai báo các trường dưới đây. pydantic-settings tự đọc biến
    môi trường theo tên trường (không phân biệt hoa thường), nên trường
    ``agent_api_key`` sẽ lấy giá trị từ biến ``AGENT_API_KEY``.

    | Trường                  | Kiểu  | Mặc định                   |
    |-------------------------|-------|----------------------------|
    | port                    | int   | 8000                       |
    | agent_api_key           | str   | KHÔNG có mặc định (bắt buộc)|
    | redis_url               | str   | "redis://localhost:6379/0" |
    | rate_limit_per_minute   | int   | 10                         |
    | monthly_budget_usd      | float | 10.0                       |
    | log_level               | str   | "INFO"                     |

    Vì sao ``agent_api_key`` không được có giá trị mặc định? Vì mặc định
    nghĩa là app vẫn khởi động khi bạn quên set secret trên cloud — và bạn
    chỉ phát hiện ra khi ai đó đã gọi API miễn phí bằng khóa mặc định đó.
    Không mặc định = fail fast ngay lúc khởi động.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    port: int = 8000
    agent_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    log_level: str = "INFO"
    # TODO (CP1): khai báo 6 trường theo bảng trên, ví dụ:
    #     port: int = 8000
    #     agent_api_key: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Đọc cấu hình một lần rồi cache lại (đọc env mỗi request là lãng phí)."""
    return Settings()
