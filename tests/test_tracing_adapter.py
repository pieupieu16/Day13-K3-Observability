from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import langfuse

from app import tracing


class FakeApp:
    class State:
        pass

    def __init__(self) -> None:
        self.state = self.State()


class RecordingTraceClient:
    def __init__(self) -> None:
        self.trace_update: dict | None = None
        self.generation_update: dict | None = None

    def update_current_trace(self, **kwargs) -> None:
        self.trace_update = kwargs

    def update_current_generation(self, **kwargs) -> None:
        self.generation_update = kwargs


class TracingAdapterTests(unittest.TestCase):
    def test_adapter_uses_the_installed_langfuse_v3_api(self) -> None:
        self.assertEqual(tracing.observe.__module__, langfuse.observe.__module__)
        client = tracing.get_langfuse_client()
        self.assertTrue(callable(client.update_current_trace))
        self.assertTrue(callable(client.update_current_generation))

    def test_tracing_is_disabled_without_both_keys(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(tracing.tracing_enabled())

        with patch.dict(os.environ, {"LANGFUSE_PUBLIC_KEY": "pk-only"}, clear=True):
            self.assertFalse(tracing.tracing_enabled())

    def test_setup_tracing_attaches_client_and_enabled_flag(self) -> None:
        client = RecordingTraceClient()
        app = FakeApp()

        with patch.object(tracing, "get_langfuse_client", return_value=client):
            with patch.object(tracing, "tracing_enabled", return_value=True):
                self.assertIs(tracing.setup_tracing(app), app)

        self.assertIs(app.state.langfuse_client, client)
        self.assertTrue(app.state.tracing_enabled)

    def test_trace_llm_call_updates_trace_and_generation(self) -> None:
        client = RecordingTraceClient()
        prompt = object()

        tracing.trace_llm_call(
            client,
            user_id_hash="user-hash",
            session_id="session-1",
            tags=["lab", "qa"],
            trace_metadata={"prompt_name": "day13-chat"},
            generation_metadata={"prompt_version": "2"},
            model="test-model",
            usage_details={"prompt_tokens": 10, "completion_tokens": 20},
            cost_details={"total": 0.01},
            prompt=prompt,
        )

        self.assertEqual(
            client.trace_update,
            {
                "user_id": "user-hash",
                "session_id": "session-1",
                "tags": ["lab", "qa"],
                "metadata": {"prompt_name": "day13-chat"},
            },
        )
        self.assertEqual(client.generation_update["model"], "test-model")
        self.assertEqual(client.generation_update["metadata"], {"prompt_version": "2"})
        self.assertIs(client.generation_update["prompt"], prompt)


if __name__ == "__main__":
    unittest.main()
