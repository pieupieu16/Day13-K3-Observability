# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Day 13 Observability - K3 Team
- Repository URL: `https://github.com/pieupieu16/Day13-K3-Observability`
- Commit SHA cuối: `8ce94b3`
- Thành viên và vai trò:
  - **Trần Hải Quân - 2A202601521** (`pieupieu16`) - Developer 1: Logging, Middleware, PII Scrubbing & Rate Limiter
  - **Nguyễn Thành Long - 2A202601443** (`kraken2811`) - Developer 2: LLM Tracing, Langfuse Adapter & Prompt Management/Rollback
  - **Đỗ Thanh Tùng - 2A202601205** (`Do Thanh Tung`) - Developer 3: Metrics Collection, Dashboard Contract (6 Panels), SLO/Alerts & Incident Lead

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** (PASSED JSON schema, Correlation ID propagation, Log enrichment & PII scrubbing)
- Tổng số traces: **15+ traces** (gửi thành công về Langfuse Cloud/Adapter)
- Số PII leak còn lại: **0** (Email, Số điện thoại VN, CCCD 12 số, Thẻ tín dụng đã được che sạch)
- Link/đường dẫn dashboard: `http://127.0.0.1:8000/dashboard`

## 3. Logging và tracing

- Evidence correlation ID: Header `x-request-id` và field `correlation_id` (ví dụ `req-130437d6`) truyền đồng nhất xuyên suốt HTTP Middleware, FastAPI Router Handler và `structlog` ContextVars.
- Evidence PII redaction: Các chuỗi nhạy cảm tự động được mã hóa đệ quy qua processor `scrub_event()` trong `app/logging_config.py` thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]`. `user_id` được hash SHA-256 (`user_id_hash`).
- Evidence trace waterfall: Langfuse Root Trace chứa các child span: `retrieve_context` (RAG search) và `llm_generation` (FakeLLM call).
- Giải thích một span đáng chú ý: Span `retrieve_context` trong thử thách `rag_slow` bị block trong 2500ms, giúp khoanh vùng thành phần RAG là nguyên nhân chính gây tăng Latency P95 từ 150ms vọt lên 2660ms.

## 4. Prompt versioning

- Prompt name: `chat_system_prompt`
- Version/label baseline: `v1` (`label: production`)
- Version/label candidate: `v2` (`label: candidate`)
- Trace ID của mỗi version: Trace metadata hiển thị rõ `prompt_version: "v1"` và `prompt_version: "v2"`.
- Bằng chứng đổi label hoặc rollback: Chuyển cờ `production` động trong `app/prompt_management.py` giữa v1 và v2 mà không cần dừng API service.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **HỢP LỆ: 6/6 panel** có trong dashboard contract.
- Evidence dashboard: Đủ 6 panel hiển thị trên `http://127.0.0.1:8000/dashboard`: P50/P95/P99 Latency, Traffic (RPS/RPM), Error Rate (%), Token Usage & Cost, Quality Proxy, và Custom Metric.
- SLO đã chọn và lý do: Target Latency P95 ≤ 2000ms và Error Rate ≤ 2.0% để đảm bảo trải nghiệm AI mượt mà cho người dùng.
- Alert rules và runbook: 
  - `HighLatencyP95`: Latency P95 > 3000ms duy trì 5 phút (Critical) -> Runbook: [docs/alerts.md#alert-1](file:///d:/Vin20k/Day13-K3-Observability/docs/alerts.md#alert-1).
  - `HighErrorRate`: Error Rate > 2.0% duy trì 5 phút (Critical) -> Runbook: [docs/alerts.md#alert-2](file:///d:/Vin20k/Day13-K3-Observability/docs/alerts.md#alert-2).
  - `CostSpike`: Total Cost > $2.5 USD trong 1 phút (Warning) -> Runbook: [docs/alerts.md#alert-3](file:///d:/Vin20k/Day13-K3-Observability/docs/alerts.md#alert-3).

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: P95 Latency của feature `refund` vọt lên ~2660ms, vượt quá ngưỡng SLO 2000ms (HighLatencyP95 alert triggered).
- Trace ID liên quan: Langfuse child span `retrieve_context` kéo dài 2500ms (chiếm 95% tổng latency request).
- Log line/correlation ID liên quan: `req-130437d6`, `req-3a280c38`, `req-5a437475`, `req-e108f7b0`, `req-a44faaad` (event `response_sent` với `latency_ms: 2661`).
- Root cause: Incident `rag_slow` được kích hoạt khiến hàm `retrieve()` trong `app/mock_rag.py` tạm dừng `time.sleep(2.5)`.
- Fix action: Gửi lệnh tắt incident `POST /incidents/rag_slow/disable` đưa thời gian phản hồi của hệ thống về lại ~150ms.
- Preventive measure: Cấu hình Strict Timeout (ví dụ max timeout 1.5s) cho truy vấn Vector Store kèm theo Fallback answer khi RAG retrieval gặp trễ.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| **Trần Hải Quân - 2A202601521** (`pieupieu16` - Dev 1) | Structured Logging JSON, Correlation ID Middleware, PII Scrubbing đệ quy, Sliding Window Rate Limiter & Kiến trúc dự án | [`d4bdb6a`](https://github.com/pieupieu16/Day13-K3-Observability/commit/d4bdb6a), [`d692f6d`](https://github.com/pieupieu16/Day13-K3-Observability/commit/d692f6d), [`76a7842`](https://github.com/pieupieu16/Day13-K3-Observability/commit/76a7842) | Structured logging với structlog, ContextVars propagation, PII Redaction đệ quy và thiết kế Rate Limiting. |
| **Nguyễn Thành Long - 2A202601443** (`kraken2811` - Dev 2) | LLM Tracing, Langfuse Adapter, Prompt Versioning (v1/v2), Production Label Tagging & Hot Rollback | [`43eaa14`](https://github.com/pieupieu16/Day13-K3-Observability/commit/43eaa14), [`PR #2`](https://github.com/pieupieu16/Day13-K3-Observability/pull/2) | Tích hợp Langfuse SDK, quản lý phiên bản Prompt v1/v2, Hot Rollback cờ production không cần redeploy ứng dụng. |
| **Đỗ Thanh Tùng - 2A202601205** (`Do Thanh Tung` - Dev 3) | Real-time Metrics Collection, 6 Panels Dashboard Contract Validator, SLO & Alert Rules, Giao diện Chat/Dashboard UI | [`0c342fd`](https://github.com/pieupieu16/Day13-K3-Observability/commit/0c342fd), [`e288b41`](https://github.com/pieupieu16/Day13-K3-Observability/commit/e288b41), [`PR #1`](https://github.com/pieupieu16/Day13-K3-Observability/pull/1), [`PR #3`](https://github.com/pieupieu16/Day13-K3-Observability/pull/3) | Thiết kế Dashboard Contract 6 panels, thu thập P50/P95 latency, error rate, token/cost và quy trình điều tra Incident. |

