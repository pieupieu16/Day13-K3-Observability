from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    class _DummyClient:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

    def get_client():
        return _DummyClient()


def get_langfuse_client():
    return get_client()


def tracing_enabled() -> bool:
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


def setup_tracing(app: Any) -> Any:
    """Attach tracing state to a FastAPI app without forcing Langfuse at startup."""
    app.state.langfuse_client = get_langfuse_client()
    app.state.tracing_enabled = tracing_enabled()
    return app


def trace_llm_call(
    client: Any,
    *,
    user_id_hash: str,
    session_id: str,
    tags: list[str],
    trace_metadata: dict[str, Any],
    generation_metadata: dict[str, Any],
    model: str,
    usage_details: dict[str, int],
    cost_details: dict[str, float],
    prompt: Any | None = None,
) -> None:
    client.update_current_trace(
        user_id=user_id_hash,
        session_id=session_id,
        tags=tags,
        metadata=trace_metadata,
    )
    client.update_current_generation(
        model=model,
        metadata=generation_metadata,
        usage_details=usage_details,
        cost_details=cost_details,
        prompt=prompt,
    )
