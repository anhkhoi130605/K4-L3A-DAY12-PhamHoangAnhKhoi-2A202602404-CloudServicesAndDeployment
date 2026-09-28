# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: điền câu trả lời chi tiết cho từng câu hỏi bên dưới.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Phạm Hoàng Anh Khôi  Mã học viên: 2A202602404

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu để giá trị mặc định là `"changeme"`, khi deploy lên production mà lập trình viên sơ suất quên cấu hình biến môi trường `AGENT_API_KEY`, ứng dụng vẫn âm thầm khởi động bình thường. Kẻ tấn công trên Internet có thể dùng từ điển hoặc thử key mặc định phổ biến `"changeme"` để gọi thành công vào endpoint `/ask`, bòn rút ngân sách token LLM hoặc khai thác tài nguyên hệ thống mà không ai hay biết cho đến khi nhận hóa đơn chi phí khổng lồ. Việc "fail fast" buộc container phải crash và dừng ngay lúc khởi động, platform sẽ lập tức gắn cờ lỗi deploy và ghi log rõ ràng, ngăn chặn việc đưa một dịch vụ không có bảo vệ lên Internet.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Dòng log JSON thu được:
```json
{"event": "ask_completed", "level": "info", "timestamp": "2026-09-28T10:15:30.123456+00:00", "user_id": "sv-test", "tokens_in": 12, "tokens_out": 35, "cost_usd": 0.000105}
```

Hai việc làm được với dòng log này mà `print("đã trả lời xong")` không làm được:
1. **Truy vấn, lọc và tổng hợp số liệu tự động bằng máy:** Các hệ thống thu thập log tập trung (như Datadog, ElasticSearch/Kibana, Grafana Loki, CloudWatch) có thể tự động parse JSON để lập chỉ mục các trường cấu trúc (`user_id`, `tokens_in`, `tokens_out`, `cost_usd`). Từ đó dễ dàng chạy truy vấn tổng hợp như: tính tổng chi phí token của user X trong ngày, hay vẽ biểu đồ số token tiêu thụ theo thời gian thực.
2. **Thiết lập cảnh báo (alerting) và phân tích bất thường tự động:** Dễ dàng cấu hình bot cảnh báo (Slack/PagerDuty) khi một sự kiện có `cost_usd > 0.05` hoặc khi `level == "error"` mà không cần viết các biểu thức chính quy (regex) phức tạp, chậm chạp và dễ gãy trên các chuỗi văn bản tự do.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.02 GB |
| Multi-stage | 148 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Phần dung lượng chênh lệch (~870 MB) là toàn bộ các công cụ biên dịch và tài nguyên phục vụ giai đoạn build không cần thiết trong runtime:
- Trình biên dịch C/C++ (`gcc`, `g++`, `make`), header files (`python3-dev`, `libc-dev`), các file build dependency dùng để biên dịch các package Python.
- Bộ nhớ đệm package của hệ điều hành (`/var/lib/apt/lists/*`), cache của pip (`~/.cache/pip`).
- Các tài liệu hướng dẫn (`man pages`), file tài liệu hệ thống và các tiện ích dòng lệnh không dùng tới có sẵn trong image đầy đủ `python:3.11`.
Trong mô hình multi-stage, stage builder chịu trách nhiệm cài đặt thư viện vào `/root/.local`, sau đó stage runtime chỉ copy thư mục package này sang image `python:3.11-slim`, giữ cho image sản phẩm gọn nhẹ và bảo mật.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

- Với Dockerfile hiện tại: Docker thực thi theo thứ tự từ trên xuống dưới và sử dụng layer cache. Các layer chuẩn bị môi trường, `COPY requirements.txt .`, và `RUN pip install` đều được dùng lại từ cache (`CACHED`). Chỉ từ layer `COPY --chown=appuser:appuser . .` (nơi phát hiện file `app/main.py` bị thay đổi checksum) cùng các layer cấu hình phía sau mới phải chạy lại. Nhờ đó, quá trình build lại chỉ mất 1-2 giây.
- Nếu đặt `COPY . .` lên trước `RUN pip install`: Khi sửa `app/main.py`, layer `COPY . .` bị đổi mã hash, làm mất hiệu lực (invalidate) toàn bộ cache của các layer phía sau nó. Docker sẽ bị ép chạy lại lệnh `RUN pip install` từ đầu, kéo lại và cài đặt lại toàn bộ dependencies trong `requirements.txt`. Việc này lãng phí băng thông mạng và kéo dài thời gian build từ vài giây lên vài phút mỗi lần sửa code.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Chuỗi sự kiện:
1. Ứng dụng Python tồn tại lỗ hổng (ví dụ Remote Code Execution thông qua deserialize dữ liệu hoặc command injection).
2. Kẻ tấn công gửi payload khai thác và giành được quyền thực thi mã shell bên trong container.
3. Vì container mặc định chạy bằng `root` (UID 0), kẻ tấn công sở hữu quyền root trong namespace của container.
4. Kẻ tấn công lợi dụng các lỗ hổng nhân Linux (kernel exploit) hoặc khai thác các volume mount nhạy cảm từ host (ví dụ mount `/var/run/docker.sock` hoặc thư mục `/etc` của host) để thực hiện "container breakout" (thoát khỏi container). Do tiến trình container trên Linux chia sẻ chung kernel với máy host và tiến trình chạy dưới UID 0, khi thoát ra ngoài, kẻ tấn công lập tức có quyền root (UID 0) trên toàn bộ máy host.

Lệnh `USER appuser` cắt đứt chuỗi tấn công ngay từ bước 3: Khi chuyển sang người dùng không có đặc quyền (non-root, ví dụ UID 1000), kẻ tấn công nếu chiếm được quyền thực thi mã trong container cũng chỉ có quyền của `appuser`. Họ không thể cài đặt thêm công cụ độc hại, không thể chỉnh sửa file hệ điều hành của container, không có quyền thao tác với docker socket và không đủ đặc quyền nhân để thực hiện các cuộc tấn công leo thang thoát khỏi container.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Con số tối đa: **20 request** trong 2 giây liên tiếp.

Giải thích:
Với cơ chế fixed window reset theo phút đồng hồ (tại giây :00):
- Tại giây thứ 59 của phút thứ nhất, người dùng gửi dồn dập 10 request (vẫn hợp lệ vì nằm trong hạn mức 10 req của phút thứ nhất).
- Đúng 1 giây sau, khi đồng hồ điểm sang giây 00 của phút thứ hai, bộ đếm bị reset về 0. Người dùng lập tức gửi tiếp 10 request nữa trong giây 00 này (vẫn hợp lệ trong hạn mức của phút thứ hai).
Kết quả là trong cửa sổ thời gian 2 giây (từ giây 59 đến giây 00), server phải xử lý tới 20 request (gấp đôi hạn mức cho phép), có thể gây sập hoặc nghẽn dịch vụ. Thuật toán sliding window (cửa sổ trượt) bằng Redis Sorted Set giải quyết triệt để lỗi này bằng cách luôn tính chính xác số request trong khoảng thời gian [t - 60s, t].

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

Khác biệt cốt lõi:
- **Rate limit**: Kiểm soát **tốc độ / tần suất gọi** API trong một khoảng thời gian ngắn (velocity / concurrency, ví dụ 10 request/phút) nhằm bảo vệ tính sẵn sàng của hạ tầng kỹ thuật, chống tấn công DoS và nghẽn tài nguyên server.
- **Cost guard**: Kiểm soát **tổng chi phí tài chính tích lũy** trong chu kỳ dài (financial budget, ví dụ $10.0/tháng theo lượng token LLM thực tế tiêu thụ) nhằm bảo vệ ngân sách dự án và ngăn ngừa tình trạng bill shock.

Tình huống rate limit cho qua nhưng cost guard chặn:
Một user gọi API rất chậm rãi, chỉ 1 request mỗi 2 phút (hoàn toàn thỏa mãn rate limit 10 request/phút). Tuy nhiên, mỗi request user này gửi một tài liệu khổng lồ hàng trăm nghìn token, khiến chi phí cộng dồn trong tháng đã chạm mốc $10.0. Khi gửi request tiếp theo, rate limit cho qua nhưng cost guard sẽ phát hiện vượt ngân sách và trả về lỗi `402 Payment Required`.

Tình huống cost guard cho qua nhưng rate limit chặn:
Một user mới đăng ký đầu tháng, tài khoản còn nguyên ngân sách $10.0 (chưa dùng đồng nào). User này viết một script gửi liên tục 15 câu hỏi ngắn trong vòng 5 giây. Ngân sách vẫn còn dư dả (cost guard không có lý do để chặn), nhưng rate limit lập tức chặn từ request thứ 11 trở đi và trả về lỗi `429 Too Many Requests` để bảo vệ server khỏi bị spam.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Thứ tự sự kiện:
1. Redis gặp sự cố gián đoạn mạng hoặc khởi động lại trong 30 giây.
2. Endpoint `/health` (đóng vai trò liveness probe) gọi kiểm tra Redis, phát hiện kết nối lỗi nên trả về status 503 hoặc timeout.
3. Bộ điều phối (Docker Compose, Kubernetes hoặc Platform Cloud) quan sát thấy liveness probe thất bại liên tiếp nên kết luận rằng tiến trình ứng dụng đã chết hoặc rơi vào deadlock.
4. Bộ điều phối lập tức ra lệnh terminate và restart lại toàn bộ 3 container agent cùng lúc.
5. Khi 3 container mới khởi động lại, Redis vẫn chưa online trở lại (vì sự cố kéo dài 30 giây). Các container mới lại kiểm tra Redis, lại thất bại ở `/health` và tiếp tục bị kill và restart lặp đi lặp lại (vòng lặp CrashLoopBackOff).
6. Mọi request của người dùng đang được xử lý dở bị đứt gãy, toàn bộ cụm dịch vụ tê liệt hoàn toàn (cascading failure).
-> Khi tách riêng: `/health` chỉ kiểm tra bản thân tiến trình Python (liveness), còn `/ready` kiểm tra Redis (readiness). Khi Redis chết, `/ready` báo 503 để load balancer tạm thời không chuyển traffic tới, nhưng container không bị restart oan uổng.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

- Khi lưu trong Redis (chuẩn Stateless): Cả 3 container agent đều chia sẻ và đọc/ghi chung một cơ sở dữ liệu Redis. Dù load balancer định tuyến request của user vào container nào (A, B hay C), `history_length` luôn tăng đều đặn theo mỗi lượt trao đổi: 0 -> 2 -> 4 -> 6...
- Nếu lưu trong dict Python (Stateful trong bộ nhớ RAM của process): Mỗi instance container có một vùng nhớ RAM tách biệt hoàn toàn:
  + Request 1 đi vào container A: lưu vào RAM của A -> response trả `history_length = 0`.
  + Request 2 được round-robin chuyển sang container B: RAM của B đang trống -> response trả `history_length = 0`.
  + Request 3 được chuyển sang container C: RAM của C cũng trống -> response trả `history_length = 0`.
  + Request 4 quay lại container A: A thấy dữ liệu từ request 1 -> response trả `history_length = 2`.
  Hậu quả là con số `history_length` sẽ nhảy lộn xộn, không liên tục và agent sẽ bị "mất trí nhớ", không thể hiểu được ngữ cảnh của cuộc hội thoại nếu request không may rơi vào instance khác.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

- **Thông báo lỗi**: `Deployment failed: Health check timed out after 300 seconds` / `Connection refused on port 8000` trên dashboard của platform.
- **Cách tìm ra nguyên nhân**: Mở mục Runtime Logs trên dashboard của platform (như Railway hoặc Render). Nhận thấy Uvicorn ghi log: `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`, trong khi platform lại cấp phát cổng động qua biến môi trường `$PORT` (ví dụ `PORT=49152`) và hệ thống reverse proxy của platform thực hiện health check tại cổng đó. Do container chỉ lắng nghe trên cổng 8000 cố định nên health check từ bên ngoài bị từ chối kết nối.
- **Cách sửa**: 
  1. Trong `app/config.py`: Đảm bảo trường port đọc từ biến môi trường `PORT` thông qua `Field(default=8000, validation_alias="PORT")`.
  2. Trong `Dockerfile`: Cấu hình khởi chạy Uvicorn bằng shell form để nội suy biến môi trường: `CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]`.
  Sau khi cập nhật và push lại mã nguồn, service đã lắng nghe đúng cổng do platform chỉ định và health check chuyển sang trạng thái 200 OK thành công.
