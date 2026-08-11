# PHÂN CHIA WORKFLOW VÀ TÁC VỤ DỰ ÁN OBSERVABILITY CHO HỆ THỐNG AI (3 NGHƯỜI)

> **Mục tiêu**: Phân chia dự án **Day 13 — Observability cho hệ thống AI** thành các phần công việc độc lập cho **3 thành viên**, đặt ra các quy tắc nghiêm ngặt (File Scoping Rules) để 3 người có thể thực hiện song song (concurrently) mà không bị xung đột code (merge conflicts).

---

## 1. TỔNG QUAN VÀ PHÂN VAI (ROLES & RESPONSIBILITIES)

Dựa trên cấu trúc 4 vai trò của dự án trong [README.md](README.md), chúng ta hợp nhất thành **3 vai trò chuyên biệt** cho nhóm 3 người:

| Thành viên | Vai trò | Phạm vi chính | Kết quả / Evidence bàn giao |
|---|---|---|---|
| **Developer 1** | **Logging, Middleware & PII Lead** | Quản lý log JSON có cấu trúc, Correlation ID, Redaction PII, Request Middleware, Log validator | - Log hợp lệ với Correlation ID & Metadata<br>- Bằng chứng che PII (Email, SĐT, Card)<br>- `validate_logs.py` ≥ 80/100 |
| **Developer 2** | **LLM Tracing & Prompt Versioning Lead** | Tích hợp Langfuse Traces/Spans, quản lý Prompt Versioning (v1/v2), Prompt Label & Rollback, Agent tracing | - Tối thiểu 10 Traces có metadata<br>- Trace gắn đúng `prompt_name/version/label`<br>- Bằng chứng thao tác Rollback/Label change |
| **Developer 3** | **Dashboard, SLO/Alert & Incident Lead** | Metrics collection, 6 panel Dashboard, SLO & Alert rules, Điều tra Challenge, Hoàn thiện Report | - Validator `validate_dashboard.py` báo 6/6 panel<br>- Ảnh Dashboard runtime đủ chỉ số<br>- Báo cáo `submission/REPORT.md` hoàn chỉnh |

---

## 2. MA TRẬN PHÂN QUYỀN FILE CỐ ĐỊNH (STRICT FILE OWNERSHIP MATRIX)

> ⚠️ **QUY TẮC VÀNG**: Mỗi thành viên **CHỈ ĐƯỢC CHỈNH SỬA** các file nằm trong phạm vi mình sở hữu. Tuyệt đối không sửa file của người khác.

```
                    ┌─────────────────────────────────────────┐
                    │      HỆ THỐNG OBSERVABILITY AI          │
                    └────────────────────┬────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
┌────────▼────────┐             ┌────────▼────────┐             ┌────────▼────────┐
│   DEVELOPER 1   │             │   DEVELOPER 2   │             │   DEVELOPER 3   │
│  Logging & PII  │             │ Traces & Prompt │             │Dashboard/Report │
└────────┬────────┘             └────────┬────────┘             └────────┬────────┘
         │                               │                               │
 ├── app/pii.py                  ├── app/tracing.py              ├── app/metrics.py
 ├── app/logging_config.py       ├── app/prompt_management.py   ├── app/challenge.py
 ├── app/middleware.py           ├── app/agent.py                ├── config/dashboard.yaml
 ├── config/logging_schema.json  ├── docs/PROMPT_VERSIONING.md   ├── config/slo.yaml
 ├── scripts/validate_logs.py    ├── tests/test_agent_*.py       ├── config/alert_rules.yaml
 ├── tests/test_pii.py           ├── tests/test_prompt_*.py      ├── scripts/validate_dashboard.py
 └── tests/test_validate_*.py    └── tests/test_tracing_*.py     ├── submission/REPORT.md
                                                                 └── tests/test_metrics.py
```

### Chi tiết phân quyền File:

#### 👤 Developer 1 (Logging & PII)
- **File sở hữu độc quyền (Write Access)**:
  - `app/pii.py`
  - `app/logging_config.py`
  - `app/middleware.py`
  - `config/logging_schema.json`
  - `scripts/validate_logs.py`
  - `tests/test_pii.py`
  - `tests/test_validate_logs.py`
- **Thư mục Evidence**: `submission/evidence/dev1_*.png` (hoặc `submission/evidence/log_*.png`)

#### 👤 Developer 2 (Tracing & Prompt Management)
- **File sở hữu độc quyền (Write Access)**:
  - `app/tracing.py`
  - `app/prompt_management.py`
  - `app/agent.py`
  - `docs/PROMPT_VERSIONING.md`
  - `tests/test_agent_prompt_trace.py`
  - `tests/test_prompt_management.py`
  - `tests/test_tracing_adapter.py`
- **Thư mục Evidence**: `submission/evidence/dev2_*.png` (hoặc `submission/evidence/trace_*.png`)

#### 👤 Developer 3 (Dashboard, Metrics, Alerts & Incident Report)
- **File sở hữu độc quyền (Write Access)**:
  - `app/metrics.py`
  - `app/challenge.py`
  - `config/dashboard.yaml`
  - `config/slo.yaml`
  - `config/alert_rules.yaml`
  - `scripts/validate_dashboard.py`
  - `submission/REPORT.md`
  - `tests/test_metrics.py`
  - `tests/test_dashboard_validator.py`
  - `tests/test_challenge_config.py`
- **Thư mục Evidence**: `submission/evidence/dev3_*.png` (hoặc `submission/evidence/dashboard_*.png`)

#### 🔒 File dùng chung / Đọc duy nhất (Read-Only Shared Files)
- `app/main.py` (*Có giao thức chỉnh sửa đặc biệt ở Mục 4*)
- `app/schemas.py`, `app/cli.py`, `app/incidents.py`, `app/mock_llm.py`, `app/mock_rag.py`
- `README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `RULES.md`, `SETUP.md`, `SUBMISSION.md`
- `requirements.txt`, `.env.example`, `.gitignore`

---

## 3. KHỐI LƯỢNG CÔNG VIỆC VÀ TIẾN ĐỘ THEO CHECKPOINT

### 🕒 Checkpoint 0 (0:00 - 0:30): Khởi tạo & Môi trường
- **Tất cả 3 người**:
  - Clone repository, cài đặt môi trường (`pip install -r requirements.txt`).
  - Đọc [SETUP.md](SETUP.md) và cấu hình `.env` cho Langfuse.
  - Chạy `uvicorn app.main:app --reload --env-file .env` và kiểm tra `/health`.

---

### 🕒 Checkpoint 1 (0:30 - 1:30): Logging, Tracing & Metrics Core

#### 👤 Developer 1: Hoàn thiện Logging & PII Redaction
1. Cấu hình `app/logging_config.py` xuất ra JSON log có cấu trúc chuẩn theo `config/logging_schema.json`.
2. Bổ sung `app/middleware.py`: Tự động sinh `correlation_id` (UUID v4) cho mỗi HTTP request và đưa vào context/headers.
3. Bổ sung `app/pii.py`: Viết regex/filter để loại bỏ Email, Số điện thoại, Số thẻ tín dụng trước khi log.
4. Chạy và sửa lỗi cho đến khi `python scripts/validate_logs.py` đạt **tối thiểu 80/100**.
5. Thu thập bằng chứng vào `submission/evidence/dev1_log_correlation.png` và `submission/evidence/dev1_pii_redact.png`.

#### 👤 Developer 2: Hoàn thiện Langfuse Tracing & Prompt Setup
1. Cấu hình `app/tracing.py` kết nối với Langfuse Client.
2. Cấu hình `app/prompt_management.py` để tạo và quản lý Prompt versions (v1/v2).
3. Đảm bảo mọi request qua `app/agent.py` đều mở trace, truyền đúng metadata (`user_id_hash`, `session_id`, `prompt_name`, `prompt_version`, `prompt_label`).
4. Chạy `python scripts/load_test.py` để sinh ra tối thiểu 10 traces trên Langfuse.

#### 👤 Developer 3: Metrics Collection & Baseline Validation
1. Hoàn thiện `app/metrics.py`: Thu thập các chỉ số request latency, error rate, token count, cost estimation.
2. Chạy baseline validation: `python scripts/validate_dashboard.py`.
3. Kiểm tra cấu hình `config/dashboard.yaml` và `config/logging_schema.json` để sẵn sàng làm phần Dashboard.

---

### 🕒 Checkpoint 2 (1:30 - 2:30): Dashboard, Prompt Versioning & Evidence

#### 👤 Developer 1: Log Verification & Support
1. Đảm bảo tất cả log sinh ra từ load test ghi đầy đủ vào `data/logs.jsonl`.
2. Kiểm tra lại PII redaction không bỏ sót các trường ẩn trong metadata.
3. Chạy `pytest tests/test_pii.py tests/test_validate_logs.py` để đảm bảo 100% pass.

#### 👤 Developer 2: Prompt Rollback & Trace Evidence
1. Thực hiện tạo Prompt v1 và v2 theo [docs/PROMPT_VERSIONING.md](docs/PROMPT_VERSIONING.md).
2. Đổi label `production` từ v1 sang v2 hoặc thực hiện Rollback.
3. Chụp các ảnh chứng minh gửi cho Dev 3 ghép báo cáo:
   - `submission/evidence/dev2_trace_waterfall.png` (Ảnh trace 10+ item)
   - `submission/evidence/dev2_prompt_versions.png` (Ảnh prompt v1/v2)
   - `submission/evidence/dev2_prompt_rollback.png` (Ảnh chuyển label/rollback)

#### 👤 Developer 3: Dựng 6 Panel Dashboard, SLO & Alert Rules
1. Chỉnh sửa `config/dashboard.yaml` để thiết kế 6 panel đúng contract:
   - Latency (p50/p95/p99)
   - Traffic (RPS/RPM)
   - Error Rate (%)
   - Token Usage & Cost
   - Quality Proxy
   - Custom Observability Metric
2. Chạy `python scripts/validate_dashboard.py` cho đến khi báo **`HỢP LỆ: 6/6 panel`**.
3. Cấu hình ngưỡng SLO trong `config/slo.yaml` và cảnh báo trong `config/alert_rules.yaml`.
4. Chụp ảnh Dashboard runtime lưu vào `submission/evidence/dev3_dashboard_6panels.png` và `submission/evidence/dev3_validator_result.png`.

---

### 🕒 Checkpoint 3 & Hoàn tất (2:30 - 4:00): Challenge Incident & Nộp Bài

#### 👤 Developer 3 (Leader buổi Challenge): Điều tra Incident & Tổng hợp Report
1. Nhận thông báo khi Lab Coach release `config/challenge.json`.
2. Chạy script incident chính thức:
   ```bash
   python scripts/inject_incident.py
   python scripts/load_test.py --challenge --concurrency 5
   ```
3. Nối luồng điều tra **Metrics → Traces → Logs**:
   - Nhìn Metrics phát hiện Panel bị spike (Latency/Error).
   - Dùng Langfuse Trace tìm span bị chậm/lỗi (lấy Trace ID).
   - Tra cứu `data/logs.jsonl` theo Trace ID/Correlation ID để tìm Log gây ra lỗi.
4. Đề xuất Root cause, phương án sửa chữa (Fix) và phòng ngừa (Preventive Action).
5. Hoàn thiện `submission/REPORT.md`.

#### 👤 Developer 1 & Developer 2 (Support Challenge & Git Cleanup):
1. Hỗ trợ Dev 3 tra cứu Log & Trace ID trong lúc điều tra incident.
2. Kiểm tra chất lượng code, loại bỏ tất cả `.env`, API key, secret khỏi git history.
3. Chạy toàn bộ test suit: `python -m pytest -q`.
4. Commit & Merge code vào branch `main`.

---

## 4. QUY TẮC CHỐNG XUNG ĐỘT KHI LÀM SONG SONG (CONCURRENCY & ANTI-CONFLICT RULES)

Để 3 người làm việc cùng lúc mà **không bị đè code (overwrite)** hay **xung đột merge (merge conflicts)**, tất cả thành viên phải tuân thủ nghiêm ngặt 5 quy tắc sau:

### 1. Git Branching Strategy
- **Không bao giờ commit trực tiếp lên `main`**.
- Mỗi người làm việc trên branch riêng đại diện cho role của mình:
  - Developer 1: `git checkout -b feat/dev1-logging-pii`
  - Developer 2: `git checkout -b feat/dev2-tracing-prompts`
  - Developer 3: `git checkout -b feat/dev3-dashboard-incident`
- Sau khi hoàn thành Checkpoint 2, từng người tạo Pull Request / Merge vào `main`.

### 2. Giao thức chỉnh sửa File chung `app/main.py` (Shared File Protocol)
`app/main.py` là file khởi tạo app FastAPI mà cả 3 người đều cần import module của mình vào. Để tránh xung đột:
- **Developer 1 (Integrator Lead cho main.py)** chịu trách nhiệm chính về cấu trúc `app/main.py`.
- **Developer 2 & 3** KHÔNG sửa trực tiếp `app/main.py` cùng lúc. Thay vào đó, viết các module theo chuẩn interface rõ ràng:
  - Dev 1 viết: `app/middleware.py` -> Expose `setup_logging_middleware(app)`
  - Dev 2 viết: `app/tracing.py` -> Expose `setup_tracing(app)`
  - Dev 3 viết: `app/metrics.py` -> Expose `setup_metrics(app)`
- Khi tích hợp vào `app/main.py`, từng người lần lượt add 1 dòng gọi hàm setup tương ứng theo thứ tự: Dev 1 -> Dev 2 -> Dev 3.

### 3. Nguyên tắc Interface Contract (Modularity)
Các module tương tác với nhau CHỈ thông qua hàm được định nghĩa sẵn, không truy cập trực tiếp biến nội bộ của nhau:
- **Dev 1 Expose**: `get_correlation_id()`, `redact_pii(text: str) -> str`
- **Dev 2 Expose**: `trace_llm_call(...)`, `get_active_prompt(...)`
- **Dev 3 Expose**: `record_request_metric(...)`, `record_token_cost(...)`

### 4. Quy tắc đặt tên File Evidence (Evidence File Naming)
Tất cả hình ảnh evidence nộp bài đặt trong `submission/evidence/` bắt buộc tuân theo prefix vai trò:
- Dev 1: `dev1_log_schema.png`, `dev1_pii_redaction.png`, `dev1_validate_logs.png`
- Dev 2: `dev2_trace_waterfall.png`, `dev2_prompt_v1_v2.png`, `dev2_prompt_rollback.png`
- Dev 3: `dev3_dashboard_6panels.png`, `dev3_validator_pass.png`, `dev3_incident_investigation.png`

### 5. Quy tắc Độc lập Test (Test Isolation)
Mỗi người chịu trách nhiệm chạy và bảo đảm pass các file test thuộc phân vùng của mình:
- Dev 1: `pytest tests/test_pii.py tests/test_validate_logs.py`
- Dev 2: `pytest tests/test_agent_prompt_trace.py tests/test_prompt_management.py tests/test_tracing_adapter.py`
- Dev 3: `pytest tests/test_metrics.py tests/test_dashboard_validator.py tests/test_challenge_config.py`

---

## 5. CHECKLIST KIỂM TRA TRƯỚC KHI NỘP BÀI (FINAL SUBMISSION CHECKLIST)

Trước khi hết giờ (mốc 3:30 - 4:00), cả 3 thành viên họp nhanh 5 phút để tích hợp:

- [ ] **Dev 1**: `python scripts/validate_logs.py` báo kết quả ≥ 80/100. Log không chứa PII (email, card, phone).
- [ ] **Dev 2**: Đã sinh 10+ traces trên Langfuse, có trace ID của Prompt v1 & v2, có bằng chứng Rollback.
- [ ] **Dev 3**: `python scripts/validate_dashboard.py` đạt `HỢP LỆ: 6/6 panel`. Đã điền đầy đủ `submission/REPORT.md`.
- [ ] **Chung**: Chạy `python -m pytest -q` trả về green (all tests passed).
- [ ] **Chung**: Chạy `git status` đảm bảo không còn secret, `.env`, `.venv/` chưa commit.
- [ ] **Chung**: Commit SHA cuối cùng đã sẵn sàng nộp lên Codelabs.

---
*File được khởi tạo tự động phục vụ bài lab Observability AI (Day 13).*
