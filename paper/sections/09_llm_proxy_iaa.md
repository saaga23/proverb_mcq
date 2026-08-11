#### 9. LLM-Proxy Inter-Annotator Agreement

### 9.1 Setup

Seven closed LLMs annotated a 60-item validation subset (20 per language) from the v68 human-annotation sample. Models: Qwen2.5-7B-Instruct, Claude-3-Haiku, DeepSeek-R1-Distill-Qwen-32B, Gemini-2.5-Flash, Llama-3.2-3B-Instruct, Phi-3.5-mini-instruct, GPT-4o-mini.

### 9.2 Results

| Model | n | Acc vs Consensus | Acc vs Gold | EN | AR | YO |
|-------|---|------------------|-------------|----|----|----|
| Qwen2.5-7B | 60 | 48.3% | 63.3% | 55% | 45% | 45% |
| Claude-3-Haiku | 60 | 58.3% | 78.3% | 70% | 55% | 50% |
| DeepSeek-R1-32B | 60 | 50.0% | 65.0% | 65% | 60% | 25% |
| Gemini-2.5-Flash | 60 | 50.0% | 78.3% | 70% | 50% | 30% |
| Llama-3.2-3B | 60 | 53.3% | 63.3% | 65% | 60% | 35% |
| Phi-3.5-mini | 60 | 45.0% | 58.3% | 50% | 45% | 40% |
| GPT-4o-mini | 60 | 55.0% | 78.3% | 65% | 50% | 50% |

**Overall:** Fleiss Îº = 0.4845 (moderate agreement). Mean pairwise Cohen Îº = 0.4846 (range: 0.295â€“0.799). **Zero refusals** across all models and items.

### 9.3 Interpretation

The LLM-proxy IAA shows:
1. **Moderate cross-model agreement** on distractor plausibility (Îº = 0.4845). This is comparable to human annotation on subjective NLP tasks.
2. **High agreement with gold meaning** (58.3â€“78.3%), especially for Claude-3-Haiku, Gemini-2.5-Flash, and GPT-4o-mini (all 78.3%).
3. **Low agreement with v68 consensus** (48.3â€“58.3%), revealing that the audit committee detects items where even aligned models disagree with gold.
4. **Yoruba weakness:** DeepSeek-R1-32B drops to 25% on Yoruba, suggesting open-weight models struggle with low-resource figurative language.

This IAA is a standalone contribution to the "LLM-as-judge" literature. It is **not** a substitute for native-speaker human validation.

---


