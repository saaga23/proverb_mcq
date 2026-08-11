"""
Local dry-run test for OpenRouter Pilot 2 v3.
Patches openrouter_chat with deterministic dict responses so no API key/credits are used.
"""

import os
import shutil
import unittest
from unittest.mock import patch

os.environ["OPENROUTER_API_KEY"] = "dummy-key-for-testing"

import openrouter_pilot_s1_s2_evaluator_v3 as pilot


def mock_openrouter_chat(model, messages, max_tokens=None, response_format=None, retries=3):
    content = messages[-1]["content"]

    if "Say the letter A" in content:
        return {
            "choices": [{"message": {"content": "A"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 1},
        }

    if "Generate 4 English answer options" in content:
        # Third option is deliberately off-length to exercise the length fallback.
        return {
            "choices": [{
                "message": {"content": '["People who start early succeed", "Those who delay often win", "X", "Morning birds eat worms"]'},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 120, "completion_tokens": 40},
        }

    if "Generate 4 proverb options" in content:
        return {
            "choices": [{
                "message": {"content": '["الصبر مفتاح الفرج", "من جد وجد", "الوقت كالسيف", "لا حول ولا قوة الا بالله"]'},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 120, "completion_tokens": 40},
        }

    # Audit
    return {
        "choices": [{"message": {"content": "A"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 80, "completion_tokens": 1},
    }


def mock_requests_get(url, timeout=30):
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            # Return every model the evaluator might ask about.
            data = [{"id": m} for m in set(pilot.GENERATOR_POOL + pilot.AUDIT_POOL)]
            return {"data": data}

    return FakeResp()


class TestPilot2v3(unittest.TestCase):
    def setUp(self):
        self.test_out = "openrouter_pilot2_output"
        pilot.OUTPUT_DIR = self.test_out
        os.makedirs(self.test_out, exist_ok=True)
        pilot.cost_tracker = pilot.CostTracker(pilot.COST_CAP_USD)
        pilot.RAW_OUTPUTS.clear()
        pilot.S1_POSITION_COUNTER = 0
        pilot.S2_POSITION_COUNTER = 0
        pilot.N_PER_LANG = 2  # tiny sample for speed
        # Disable the sentence-transformer guard in local tests to avoid slow model loading.
        pilot._SEMANTIC_MODEL = False

    def tearDown(self):
        if os.path.exists(self.test_out):
            shutil.rmtree(self.test_out)

    @patch("requests.get", side_effect=mock_requests_get)
    @patch.object(pilot, "openrouter_chat", side_effect=mock_openrouter_chat)
    def test_end_to_end(self, _mock_chat, _mock_get):
        pilot.main()

        self.assertTrue(os.path.exists(os.path.join(self.test_out, "mcqs_s1.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "mcqs_s2.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot2_eval_results.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot2_summary.json")))
        self.assertTrue(os.path.exists(os.path.join(self.test_out, "pilot2_state.json")))

        s1 = pilot.pd.read_csv(os.path.join(self.test_out, "mcqs_s1.csv"))
        s2 = pilot.pd.read_csv(os.path.join(self.test_out, "mcqs_s2.csv"))
        self.assertEqual(len(s1), 6)  # 3 languages × 2
        self.assertEqual(len(s2), 6)
        self.assertIn("generation_status", s1.columns)
        self.assertIn("generation_status", s2.columns)


if __name__ == "__main__":
    unittest.main(verbosity=2)
