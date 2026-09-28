# K4 — Level 3A, Ngày 12: Hạ Tầng Cloud & Deployment (240 phút)

![CI](https://github.com/anhkhoi130605/K4-L3A-DAY12-PhamHoangAnhKhoi-2A202602404-Cloud-Service-And-Deployment/actions/workflows/ci.yml/badge.svg)

Đưa một AI agent từ `localhost:8000` lên một địa chỉ công khai mà người khác
gọi được, có bảo mật, có giới hạn chi phí, và không sập khi bạn deploy bản mới.

---

## ⚠️ Bài Làm Cá Nhân

**Đây là bài tập cá nhân. Mỗi học viên nộp một repository của riêng mình.**

Tài liệu chính thức của bài lab:

- [SUBMISSION.md](SUBMISSION.md) — cấu trúc bài nộp, tên repo và nơi nộp
- [RUBRIC.md](RUBRIC.md) — tiêu chí chấm, bằng chứng và điều kiện mất điểm
- [CHECKPOINTS.md](CHECKPOINTS.md) — sản phẩm, kiến thức và cách tự kiểm tra từng checkpoint
- [RULES.md](RULES.md) — quy định làm bài, dùng AI, hợp tác và bảo mật

| Được phép | Không được phép |
|-----------|-----------------|
| Đọc tài liệu, Stack Overflow, tra AI để hiểu khái niệm | Sao chép code của học viên khác |
| Hỏi Lab Coach khi bị kẹt | Dùng chung repo, chung commit history |
| Thảo luận **cách tiếp cận** với bạn cùng lớp | Nhờ người khác làm hộ, kể cả một phần |
| Dùng AI để giải thích lỗi | Nộp code mà bạn không giải thích được |

**Cách kiểm tra:** Lab Coach sẽ chọn ngẫu nhiên học viên để hỏi
trực tiếp về code trong bài nộp. Không giải thích được phần mình viết → điểm
phần đó bị hủy.

**Phát hiện hai bài trùng nhau bất thường (cùng lỗi chính tả, cùng comment,
cùng cấu trúc lạ): cả hai bài đều 0 điểm**, không phân biệt ai chép của ai.

---

## 📦 Cách Đặt Tên Repository

Repo nộp bài **bắt buộc** đặt tên theo mẫu:

```
K4-L3A-DAY12-<HoVaTen>-<MSSV>-<TenBai>
```

**Quy tắc viết:**
- Họ tên **viết liền, không dấu**, chữ cái đầu mỗi từ viết hoa
- Ngăn cách các phần bằng dấu gạch ngang `-`
- Không khoảng trắng (GitHub tự đổi khoảng trắng thành `-`, dễ sai lệch)
- `TenBai` của lab này là `CloudServicesAndDeployment`

**Ví dụ:**

| Học viên | Tên repo |
|----------|----------|
| L3A202600280 — Nguyễn Văn An | `K4-L3A-DAY12-NguyenVanAn-L3A202600280-CloudServicesAndDeployment` |
| L3A202601111 — Trần Thị Bích Hà | `K4-L3A-DAY12-TranThiBichHa-L3A202601111-CloudServicesAndDeployment` |

**Sai tên repo = trừ 5 điểm.** Đây là cách duy nhất để Lab Coach biết bài của ai
trong khoảng 1000 repo.

### Tạo repo và bắt đầu làm

```bash
# 1. Fork repo lab về và đổi tên theo cú pháp bên trên
# 2. Clone repo lab về máy
git clone <URL repo bạn đã fork>
cd K4-L3A-DAY12-NguyenVanAn-L3A202600280-CloudServicesAndDeployment

# 3. Commit và Push khi hoàn thiện bài lab
git add .
git commit -m "Checkpoint 0"
git push origin main
```

> Commit sau mỗi checkpoint. Lịch sử commit cho thấy bạn tự làm — một commit
> duy nhất vào phút chót là dấu hiệu đáng ngờ.

---

## Mục Tiêu

Sau buổi lab này, bạn sẽ:
- Tách toàn bộ cấu hình ra khỏi code theo 12-Factor và biết vì sao secret không được có giá trị mặc định
- Viết Dockerfile multi-stage, chạy container bằng user thường, image dưới 500MB
- Bảo vệ API bằng API key, sliding-window rate limit và cost guard theo tháng
- Phân biệt liveness/readiness probe, xử lý SIGTERM để deploy không rớt request
- Thiết kế service stateless để scale ngang được
- Deploy lên cloud và có một địa chỉ công khai hoạt động thật

---

## Lịch Trình & Checkpoint

| Thời gian từ lúc bắt đầu | Nội dung | Checkpoint | Điểm |
|-----|----------|------------|------|
| Start +0–20 phút | Setup môi trường, tạo repo đúng tên | **CP0 tại Start +20 phút:** `pytest tests/ -v` chạy được (rớt hết là đúng — bạn chưa code) | — |
| Start +20–60 phút | **Block 1** — 12-Factor Config, Health, Logging | **CP1 tại Start +60 phút:** `pytest tests/test_cp1.py -v` | 15 |
| Start +60–105 phút | **Block 2** — Docker: multi-stage, bảo mật image | **CP2 tại Start +105 phút:** `pytest tests/test_cp2.py -v` | 15 |
| Start +105–115 phút | ☕ Giải lao | — | — |
| Start +115–160 phút | **Block 3** — API Security: auth, rate limit, cost guard | **CP3 tại Start +160 phút:** `pytest tests/test_cp3.py -v` | 20 |
| Start +160–200 phút | **Block 4** — Scaling & Reliability | **CP4 tại Start +200 phút:** `pytest tests/test_cp4.py -v` | 20 |
| Start +200–230 phút | **Block 5** — Deploy lên cloud | **CP5 tại Start +230 phút:** `pytest tests/test_cp5.py -v` | 15 |
| Start +230–240 phút | Hoàn thiện `exercises.md`, `python grade.py`, nộp bài | | 15 |
| — | **BONUS** — CI/CD với GitHub Actions (không bắt buộc) | `pytest tests/test_bonus_cicd.py -v` | +10 |

**Cách dùng checkpoint:** ghi nhận thời điểm buổi lab bắt đầu là `Start`, sau đó
chạy lệnh checkpoint tại mốc `Start + N phút` tương ứng. Xanh hết → sang block
sau. Còn đỏ → đọc thông báo lỗi (mỗi test đều ghi rõ sai ở đâu và vì sao điều
đó quan trọng), sửa, chạy lại. Kẹt quá 10 phút thì gọi Lab Coach và **đi tiếp
block sau** — làm được đến đâu có điểm đến đó, đừng để tắc một chỗ mà mất cả
các block còn lại.

**Phần BONUS** dành cho bạn nào xong sớm hoặc muốn làm thêm sau buổi lab: tự
viết một workflow GitHub Actions để mỗi lần push là tự chạy test, tự build
image, và chỉ deploy khi mọi thứ xanh. Lab **không cho sẵn file mẫu** — đây là
phần để bạn tự đọc tài liệu và tự dựng. Chỉ nên bắt đầu khi CP1–CP5 đã ổn.
Tổng bonus của bài lab tối đa **10 điểm**; đây là điểm cho sản phẩm CI/CD của
bài lab, không phải điểm giơ tay, phát biểu hay pitching trên lớp.

Chi tiết từng bước: [LAB_GUIDE.md](LAB_GUIDE.md).

---

## Cài Đặt

### Yêu cầu
- Python 3.11+
- Docker & Docker Compose (cần cho CP2 trở đi)
- Git + tài khoản GitHub
- Tài khoản Railway hoặc Render (miễn phí, đăng ký ~5 phút — cần cho CP5)

Không cần API key của OpenAI hoặc các bên cung cấp API khác: lab dùng **mock LLM** chạy offline.

### Môi trường ảo & thư viện

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### File cấu hình

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

Mở `.env`, đổi `AGENT_API_KEY` thành khóa của riêng bạn:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` đã nằm trong `.gitignore` — **không bao giờ commit file này**.

### Redis

```bash
docker compose up -d redis            # cách chuẩn
```

Chưa cài được Docker? Đặt tạm `REDIS_URL=fake://` trong `.env` để dùng Redis giả
trong RAM (đủ để làm CP1/CP3/CP4, nhưng CP2 và CP5 vẫn cần Docker).

---

## Cấu Trúc Thư Mục

```
K4-L3A-DAY12-<HoVaTen>-<MSSV>-CloudServicesAndDeployment/
├── README.md              # File này — quy định, lịch trình, chấm điểm, nộp bài
├── LAB_GUIDE.md           # Hướng dẫn chi tiết từng block
├── exercises.md           # 10 câu phản ánh
├── DEPLOYMENT.md          # Điền URL sau khi deploy (CP5 đọc file này)
├── grade.py               # Chấm điểm tự động
├── app/                   # ★ NƠI BẠN VIẾT CODE
│   ├── config.py          #   CP1 — Settings 12-factor
│   ├── logging_utils.py   #   CP1 — log JSON
│   ├── main.py            #   CP1/CP3/CP4 — FastAPI app
│   ├── auth.py            #   CP3 — xác thực API key
│   ├── rate_limiter.py    #   CP3 — sliding window
│   ├── cost_guard.py      #   CP3 — ngân sách theo tháng
│   ├── store.py           #   CP4 — lịch sử hội thoại trong Redis
│   └── lifecycle.py       #   CP4 — graceful shutdown
├── utils/mock_llm.py      # Cho sẵn — LLM giả, không cần API key
├── Dockerfile             # ★ CP2 — sửa thành multi-stage
├── docker-compose.yml     # ★ CP2 — thêm service agent
├── .dockerignore          # ★ CP2 — bổ sung mục còn thiếu
├── nginx/nginx.conf       # Cho sẵn — mở rộng tùy chọn về load balancing
├── railway.toml           # CP5 — cấu hình Railway
├── render.yaml            # CP5 — cấu hình Render
├── screenshots/           # Ảnh chụp màn hình bản deploy
├── .github/workflows/     # ★ BONUS — workflow CI/CD bạn tự viết (chưa có sẵn)
└── tests/
    ├── test_cp1.py … test_cp5.py
    ├── test_bonus_cicd.py # BONUS — chấm workflow CI/CD
    └── conftest.py
```

Dấu ★ = file bạn phải sửa (hoặc tự tạo). Các file khác đọc để hiểu, không cần sửa.

---

## Chạy Kiểm Thử

```bash
pytest tests/test_cp1.py -v     # từng checkpoint
pytest tests/ -v                # toàn bộ
pytest tests/ -v -m "not docker"  # bỏ qua test build Docker (chậm)
```

Test dùng Redis giả (`fakeredis`) nên **không cần Redis thật**. Các test build
image tự bỏ qua nếu máy bạn chưa bật Docker.

---

## Chấm Điểm Tự Động (100 điểm)

```bash
python grade.py
```

| Tiêu chí | Cách chấm | Điểm |
|----------|-----------|------|
| CP1 — 12-Factor Config, Health & Logging | `tests/test_cp1.py` | 15 |
| CP2 — Docker: multi-stage, bảo mật image | `tests/test_cp2.py` | 15 |
| CP3 — API Security: auth, rate limit, cost guard | `tests/test_cp3.py` | 20 |
| CP4 — Scaling & Reliability | `tests/test_cp4.py` | 20 |
| CP5 — Cloud Deployment | `tests/test_cp5.py` | 15 |
| `exercises.md` — 10 câu phản ánh | Đếm số câu đã trả lời | 15 |
| **Tổng phần bắt buộc** | | **100** |
| BONUS — CI/CD với GitHub Actions | `tests/test_bonus_cicd.py` | +10 |

Tổng bonus của bài lab tối đa **10 điểm** và tổng cuối không vượt quá 100.
Bonus này chỉ chấm sản phẩm CI/CD của bài lab, không phải điểm giơ tay, phát
biểu hay pitching. Muốn chấm nhanh phần bắt buộc thôi: `python grade.py
--no-bonus`.

Điểm mỗi checkpoint tỷ lệ với số test pass — **làm được đến đâu có điểm đến đó**.

**Trừ điểm:**
- Sai quy tắc đặt tên repo: **−5**
- Commit file `.env` hoặc để lộ API key trong repo: **−10**
- Không giải thích được code khi được hỏi: hủy điểm phần đó

**Không deploy được lên cloud?** Đặt `LOCAL_FALLBACK=true` trong `.env`, chạy
`docker compose up -d`, chụp màn hình vào `screenshots/`. CP5 khi đó tối đa
9/15 điểm. Vẫn hơn là bỏ trắng.

---

## Hướng Dẫn Nộp Bài

```bash
# 1. Kiểm tra lần cuối
python grade.py

# 2. Chắc chắn .env KHÔNG bị commit
git status --porcelain | grep -q "\.env$" && echo "DỪNG LẠI: .env đang bị theo dõi"

# 3. Commit và đẩy lên
git add -A
git commit -m "Hoàn thành lab Day 12"
git push
```

Nộp **link repository** lên Codelab. Repo phải ở chế độ public.

---

## Danh Sách Kiểm Tra Trước Khi Nộp

- [ ] Repo đúng tên `K4-L3A-DAY12-<HoVaTen>-<MSSV>-CloudServicesAndDeployment`
- [ ] `pytest tests/ -v` — đã chạy và biết rõ test nào còn rớt, vì sao
- [ ] `python grade.py` — xem điểm, mục tiêu ≥ 75/100
- [ ] `exercises.md` — đủ 10 câu, viết bằng lời của mình
- [ ] `DEPLOYMENT.md` — có Public URL thật, không dán giá trị API key
- [ ] `screenshots/` — có ảnh dashboard và ảnh gọi `/health`
- [ ] `.env` **không** nằm trong repo (`git ls-files | grep .env` chỉ ra `.env.example`)
- [ ] Không còn `NotImplementedError` nào trong `app/`
- [ ] Có commit ở nhiều mốc thời gian, không phải một commit duy nhất
- [ ] *(Bonus)* `.github/workflows/ci.yml` chạy xanh, README có badge `passing`
