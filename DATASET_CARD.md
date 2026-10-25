# ProverbGap Dataset Card

## Dataset Description

ProverbGap is a cross-lingual multiple-choice question (MCQ) benchmark for proverb understanding across English, Arabic, and Yoruba. The **v68 production dataset** contains 180 MCQs (N=5 per language: 15 proverbs, 4 variants, 3 generators). This card also describes the source proverb corpora used for generation and fallback sampling.

**v68 production dataset (canonical):**
- 180 total MCQs: 60 English, 60 Arabic, 60 Yoruba

**Source corpora (for generation and fallback):**

| Language | Source file | Cleaned count | Sampled for v68 |
|----------|------------|--------------|-----------------|
| English | `actual_data/English_cleaned.csv` | 2,278 | 15 proverbs (5 per language) |
| Arabic | `actual_data/Arabic_cleaned.csv` | 913 | 15 proverbs (5 per language) |
| Yoruba | `actual_data/Yoruba_cleaned.csv` | 3,974 | 15 proverbs (5 per language) |

**Note:** Earlier dataset card versions referenced French (161), German (142), and Spanish (63) proverb files. These files are **not present** in `actual_data/` and are not used by the v68 pipeline. The previously stated total of 7,172 is corrected to 7,165 (English 2,278 + Arabic 913 + Yoruba 3,974).

## Collection Methodology

### English Proverbs
Sourced from public-domain proverb compilations (scraped). Specific source URLs were not recovered and are documented as a provenance gap. See `DATA_PROVENANCE_TEMPLATE.md`.

Sample IDs use `ENG` prefix.

### Arabic Proverbs
Sourced from an academic dataset using `MID` prefix sample IDs. The original dataset source has not been identified; licensing is under review.

### Yoruba Proverbs
Sourced from *Yoruba Proverbs* by Oyekan Owomoyela (University of Nebraska Press, 2005, ISBN 978-0-8032-1843-7). This source is **copyrighted**. No redistribution permission has been obtained. Of the 3,974 cleaned Yoruba rows, 3,834 have missing QA_Flag and 3,748 have missing Comments.

Sample IDs use `YOR` prefix.

## Known Limitations

1. **Dialectal homogeneity**: Arabic proverbs are primarily MSA/fus-ha. Dialectal variation (Egyptian, Levantine, Gulf, Maghrebi) is not labeled or balanced.
2. **Size imbalance**: Yoruba has ~4.1x more source proverbs than Arabic. This reflects collection availability, not intentional design.
3. **Contamination risk**: English proverbs include canonical sayings likely present in LLM pre-training corpora.
4. **Translation quality**: English translations of Yoruba and Arabic proverbs are interpretive. No inter-annotator agreement was computed.
5. **No temporal metadata**: Proverbs are not dated.
6. **Data rights (CRITICAL)**: See the Licensing section below. The data release is blocked pending provenance/rights review.

## License

**Code:** Licensed under the MIT License (see `LICENSE`).

**Data:** **BLOCKED PENDING PROVENANCE/RIGHTS REVIEW.** The v68 MCQ dataset is not released under CC BY 4.0. See the `LICENSE` file for the full data-rights status:

- **English**: Scraped from public-domain sources, but specific URLs were not recovered. Rights status provisional.
- **Arabic**: Source dataset unidentified. Rights status unknown.
- **Yoruba**: Derived from Owomoyela (2005), copyrighted. No redistribution permission obtained. The public v68 CSV (`pilot1_test_generated_mcqs.csv`) currently contains 60 Yoruba MCQ rows, exposing this restricted data. This is documented as an unresolved issue.

**Recommended citation**: Abraham, S.A. (2026). ProverbGap: Hardened Adversarial Distractor Generation for Low-Resource Figurative Language. EACL 2027 ARR submission.

## Usage

The v68 dataset is intended for:
- Benchmarking LLM understanding of figurative language
- Cross-lingual evaluation of cultural knowledge
- Distractor generation research for low-resource languages

Not intended for:
- High-stakes testing or assessment
- Commercial applications without additional validation
- Automated cultural knowledge screening

## Ethics Statement

This dataset was compiled from publicly available proverb collections with the goal of surfacing cultural knowledge that Western-centric benchmarks often overlook. We acknowledge that:
- Proverbs are communal cultural property of their respective language communities
- Benchmarking should benefit, not exploit, these communities
- Native speaker validation is essential for meaningful evaluation
- Results should not be used to make claims about group-level cultural competence

## Maintenance

This is a pilot-scale release (N=5 per language evaluated). A full-scale release (N=30+ per language) with train/dev/test splits is planned **pending rights resolution**.

## Contact

For questions or corrections, please open an issue in the repository.
