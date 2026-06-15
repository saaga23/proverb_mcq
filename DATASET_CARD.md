# ProverbGap Dataset Card

## Dataset Description

ProverbGap is a cross-lingual multiple-choice question (MCQ) benchmark for proverb understanding across English, Arabic, and Yoruba. It contains 7,172 proverbs with translations and cultural explanations, designed to evaluate LLM comprehension of figurative language in high- and low-resource settings.

- **English**: 2,278 proverbs with meanings
- **Arabic**: 913 proverbs with English translations and cultural contexts
- **Yoruba**: 3,931 proverbs with English translations and cultural contexts
- **French**: 161 proverbs (not used in current benchmark)
- **German**: 142 proverbs (not used in current benchmark)
- **Spanish**: 63 proverbs (not used in current benchmark)

## Collection Methodology

### English Proverbs
Sourced from public proverb collections and reference works. Each proverb includes an explanatory meaning written in English. Sample IDs use `ENG` prefix.

### Arabic Proverbs
Sourced from classical Arabic proverb collections (amsal). Each entry includes:
- Original Arabic text (MSA/fus-ha)
- English translation
- Cultural context explaining the proverb's usage and significance

Sample IDs use `MID` prefix. The collection focuses on Standard Arabic wisdom sayings rather than specific dialectal variants.

### Yoruba Proverbs
Sourced from Yoruba oral tradition collections and ethnographic records. Each entry includes:
- Original Yoruba text (with tonal marks where available)
- English translation
- Cultural context explaining the proverb's meaning and usage

Sample IDs use `YOR` prefix.

## Known Limitations

1. **Dialectal homogeneity**: Arabic proverbs are primarily MSA/fus-ha. Dialectal variation (Egyptian, Levantine, Gulf, Maghrebi) is not labeled or balanced.
2. **Size imbalance**: Yoruba has 4x more proverbs than Arabic. This reflects collection availability, not intentional design.
3. **Contamination risk**: English proverbs include canonical sayings (e.g., "A bird in the hand") likely present in LLM pre-training corpora.
4. **Translation quality**: English translations of Yoruba and Arabic proverbs are interpretive. No inter-annotator agreement was computed.
5. **No temporal metadata**: Proverbs are not dated, making it impossible to create temporal train/test splits.

## License

This dataset is released for research purposes. Proverb texts are considered communal cultural knowledge. Translations and explanations are provided for research evaluation.

**Recommended citation**: If you use this dataset, please cite the ProverbGap paper (forthcoming).

## Usage

The dataset is intended for:
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

This is a pilot-scale release (N=5 per language evaluated). A full-scale release (N=30+ per language) with train/dev/test splits is planned.

## Contact

For questions or corrections, please open an issue in the repository.
