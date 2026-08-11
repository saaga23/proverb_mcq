"""
Local dry-run test for the Pilot 1 Nano + Opus + Qwen test variant.
Patches openrouter_chat with deterministic responses so no API key/credits are used.
"""

import os
import sys
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock

os.environ["OPENROUTER_API_KEY"] = "dummy-key-for-testing"

import openrouter_pilot_distractor_generation_test_nano_opus as pilot


class MockResponse:
    def __init__(self, text, prompt_tokens=100, completion_tokens=50, finish_reason="stop"):
        self._text = text
        self._prompt = prompt_tokens
        self._completion = completion_tokens
        self._finish = finish_reason

    def json(self):
        return {
            "choices": [{"message": {"content": self._text}, "finish_reason": self._finish}],
            "usage": {"prompt_tokens": self._prompt, "completion_tokens": self._completion},
        }

    def raise_for_status(self):
        pass


def mock_openrouter_chat(model, messages, max_tokens=None, response_format=None, retries=3):
    content = messages[-1]["content"]

    # Generation/probe call: return a JSON list of 4 strings, with one off-length distractor
    if "JSON" in content or "json" in content or "Generate" in content or "generate" in content or "Options" in content or "options" in content:
        return MockResponse(
            '["People who start early succeed", "Those who delay often win", "X", "Morning birds eat worms"]',
            prompt_tokens=120,
            completion_tokens=40,
        ).json()

    # Audit call: always pick the correct label (A)
    return MockResponse("A", prompt_tokens=80, completion_tokens=1).json()


class TestPilot1NanoOpus(unittest.TestCase):
    def setUp(self):
        self.test_out = "openrouter_pilot1_test_output_test"
        pilot.OUTPUT_DIR = self.test_out
        os.makedirs(self.test_out, exist_ok=True)
        pilot.RAW_OUTPUTS.clear()
        pilot.cost_tracker = pilot.CostTracker(pilot.COST_CAP_USD)

    def tearDown(self):
        if os.path.exists(self.test_out):
            shutil.rmtree(self.test_out)

    @patch.object(pilot, "openrouter_chat", side_effect=mock_openrouter_chat)
    def test_end_to_end(self, _mock):
        pilot.main()

        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot1_test_generated_mcqs.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot1_test_audit_results.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot1_test_prompt_comparison.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot1_test_raw_outputs.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot1_test_summary.json")))

        # Check that raw outputs were captured
        raw_df = pilot.pd.read_csv(os.path.join(self.test_out, "pilot1_test_raw_outputs.csv"))
        self.assertGreater(len(raw_df), 0)
        self.assertIn("stage", raw_df.columns)
        self.assertIn("generator_model", raw_df.columns)

        # Check that some MCQs were generated (not all fallback)
        mcqs = pilot.pd.read_csv(os.path.join(self.test_out, "pilot1_test_generated_mcqs.csv"))
        self.assertTrue(mcqs["generation_status"].isin(["generated", "partial"]).any())
        # All active generators should appear in the output
        self.assertTrue(set(mcqs["generator_model"].unique()).issubset(set(pilot.generator_pool.active)))
        # Audit committee has at least 3 reliable models
        self.assertGreaterEqual(len(pilot.committee_pool.active), 3)

        # Audit extracted A correctly (mock always returns A)
        audit = pilot.pd.read_csv(os.path.join(self.test_out, "pilot1_test_audit_results.csv"))
        self.assertEqual(audit["consensus_label"].iloc[0], "A")


if __name__ == "__main__":
    unittest.main(verbosity=2)
