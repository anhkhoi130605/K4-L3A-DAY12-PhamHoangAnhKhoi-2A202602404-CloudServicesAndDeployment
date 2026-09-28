# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Phạm Hoàng Anh Khôi |
| Mã học viên | 2A202602404 |
| Repo | https://github.com/anhkhoi130605/K4-L3A-DAY12-PhamHoangAnhKhoi-2A202602404-Cloud-Service-And-Deployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-agent-anhkhoi.onrender.com |
| Platform | Render |
| Ngày deploy | 28/09/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán động |
| `AGENT_API_KEY` | ✅ | đặt trong dashboard Settings, không lưu trong repo |
| `REDIS_URL` | ✅ | Redis add-on nội bộ của Render (day12-redis) |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

Thay `<URL>` bằng Public URL ở trên:

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i https://day12-agent-anhkhoi.onrender.com/health

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i https://day12-agent-anhkhoi.onrender.com/ready

# 3. Không có API key — mong đợi 401
curl -i -X POST https://day12-agent-anhkhoi.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST https://day12-agent-anhkhoi.onrender.com/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST https://day12-agent-anhkhoi.onrender.com/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo
```

## Kết Quả Chạy Thật

Dán output của các lệnh trên vào đây:

```
1. Liveness:
HTTP/1.1 200 OK
content-type: application/json
{"status":"ok","service":"day12-agent","version":"1.0.0"}

2. Readiness:
HTTP/1.1 200 OK
content-type: application/json
{"status":"ready","redis":true}

3. Không có API key:
HTTP/1.1 401 Unauthorized
{"detail":"Missing API key"}

4. Có API key:
HTTP/1.1 200 OK
content-type: application/json
{"answer":"Deploy là quá trình đưa ứng dụng từ môi trường phát triển lên máy chủ...","user_id":"sv-test","history_length":0,"cost_usd":0.0001,"tokens":{"in":12,"out":35}}

5. Rate limit:
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform
- `screenshots/health.png` — kết quả gọi `/health` từ trình duyệt hoặc curl

