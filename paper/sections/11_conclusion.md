#### 11. Conclusion

We presented ProverbGap, a hardened adversarial distractor-generation pipeline for proverb MCQs in English, Arabic, and Yoruba. The pipeline achieves zero infrastructure failures but fails all shortcut-resistance gates except duplicates and key balance. The central finding is that the corpus-based fallback sampler is the critical bottleneck: 43.9% of MCQs require fallback replacements, and 27.8% become high-consensus-wrong items due to confident-wrong corpus distractors.

We documented six failure modes: generic reversal/idiom shortcut, NLI over-filtering, confident-wrong corpus fallback, cultural mismatch in low-resource languages, variant triviality, and committee position bias. A cross-lingual gradient emerges: Arabic requires 3.5Ã— more fallback replacements than English, suggesting the pipeline is calibrated for high-resource languages.

LLM-proxy inter-annotator agreement across seven models yields Fleiss Îº = 0.4845 (moderate agreement) and 58.3–78.3% match to curated gold meanings (mean 69.4%). This is a standalone contribution to LLM-as-judge methodology, not a substitute for human validation.

We release the pipeline, audit logs, and 180 MCQs as a public testbed for reproducible distractor-generation research, at a production cost of $0.85 ($0.0047 per audited MCQ).

**Future work:** (1) Enable LLM-based fallback generation (v69/v70 ablation) to replace the corpus sampler. (2) Recruit native speakers for human validation with IAA reporting. (3) Scale to N=15 per language (540 MCQs). (4) Extend to fill-in-the-blank and open-ended generation tasks. (5) Add position shuffling to eliminate committee position bias.

---


