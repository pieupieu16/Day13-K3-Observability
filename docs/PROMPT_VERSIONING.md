# Prompt Versioning

Muc tieu cua Task 2 la dam bao moi request co the truy vet prompt version da dung, doi label an toan va rollback duoc khi version moi gay loi. Phan nay khong cham prompt hay hon, chi cham kha nang quan ly version va bang chung tracing.

## Prompt Contract

Tao text prompt tren Langfuse voi ten mac dinh:

```text
day13-chat
```

Prompt phai giu dung ba bien sau:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

Ung dung doc prompt theo hai bien moi truong:

```dotenv
LANGFUSE_PROMPT_NAME=day13-chat
LANGFUSE_PROMPT_LABEL=production
```

Neu Langfuse khong kha dung, app dung local fallback trong `app/prompt_management.py`. Trace metadata se ghi `prompt_source=local` hoac `prompt_source=local-fallback` de khong gia vo da lay duoc managed prompt.

## Version Can Tao

Tao it nhat hai version:

- Version 1: template baseline, gan labels `baseline` va `production`.
- Version 2: thay doi nho ve format hoac huong dan do dai cau tra loi, gan label `candidate`.

Goi y version 2:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}

Answer in 3 concise bullet points and cite the most relevant retrieved context.
```

## Quy Trinh Kiem Tra

1. Cai bien moi truong de chay version baseline:

```powershell
$env:LANGFUSE_PROMPT_NAME="day13-chat"
$env:LANGFUSE_PROMPT_LABEL="baseline"
python scripts/load_test.py
```

2. Cai bien moi truong de chay version candidate:

```powershell
$env:LANGFUSE_PROMPT_NAME="day13-chat"
$env:LANGFUSE_PROMPT_LABEL="candidate"
python scripts/load_test.py
```

3. Mo Langfuse va kiem tra trace metadata co day du:

- `prompt_name`
- `prompt_label`
- `prompt_version`
- `prompt_source`

4. Doi label `production` sang version 2 tren Langfuse, sau do chay lai:

```powershell
$env:LANGFUSE_PROMPT_LABEL="production"
python scripts/load_test.py
```

5. Rollback label `production` ve version 1 neu can, roi chup anh bang chung.

## Metadata Duoc Gan Vao Trace

`app/agent.py` gan metadata prompt vao ca trace va generation:

- `prompt_name`
- `prompt_label`
- `prompt_version`
- `prompt_source`

Generation co them:

- `doc_count`
- `query_preview`
- `prompt_fetch_error`

## Interface Code

Developer 2 expose cac interface sau:

- `app.tracing.setup_tracing(app)`
- `app.tracing.trace_llm_call(...)`
- `app.prompt_management.get_active_prompt(...)`

`setup_tracing(app)` chi gan client va enabled flag vao `app.state`; ham nay khong bat buoc app phai ket noi Langfuse thanh cong tai startup.

## Evidence Can Nop

Luu anh vao `submission/evidence/`:

- `dev2_trace_waterfall.png`: man hinh co it nhat 10 traces.
- `dev2_prompt_v1_v2.png`: man hinh co prompt version 1 va version 2.
- `dev2_prompt_rollback.png`: man hinh doi label hoac rollback `production`.

Trong bao cao, ghi lai:

- Trace ID cua request dung version 1.
- Trace ID cua request dung version 2.
- Label nao dang tro den version nao sau khi rollback.

## Test Rieng Cua Developer 2

Chay:

```bash
pytest tests/test_agent_prompt_trace.py tests/test_prompt_management.py tests/test_tracing_adapter.py
```

Tat ca test nay phai pass truoc khi merge.
