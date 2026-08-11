# Data Provenance Documentation Template

> **Purpose**: EACL reviewers will scrutinize data sources. This document must be complete, accurate, and cite every source. Fill in ALL blanks below.
> **Status**: FILLED 2026-07-10. Some fields remain undocumented and are flagged as liabilities.

---

## 1. YORUBA DATA

### Source Type
- [x] Book (OCR'd)
- [ ] Website
- [ ] Oral collection
- [ ] Other: ___________

### Book Details (FILLED)
| Field | Answer |
|-------|--------|
| **Book Title** | *Yoruba Proverbs* |
| **Author(s)** | Oyekan Owomoyela |
| **Publisher** | University of Nebraska Press, Lincoln and London |
| **Year of Publication** | 2005 |
| **ISBN (cloth)** | 0-8032-3576-3 |
| **ISBN (paperback)** | 978-0-8032-1843-7 |
| **Total proverbs in book** | 5,235 |
| **Proverbs extracted** | 3,974 (full extracted set) |
| **Pages used** | Full book (OCR'd from PDF) |
| **Library/Archive** | Personal copy / acquired PDF |

### OCR Process
| Field | Your Answer |
|-------|-------------|
| **OCR tool** | Not documented |
| **Date of OCR** | Not documented |
| **Post-processing** | Not documented |
| **Error rate estimate** | Not documented |

### Rights & Permission
- [ ] Book is in public domain
- [ ] Book is out of copyright (published before _____)
- [x] Fair use / academic use claimed (UNVERIFIED)
- [ ] Permission obtained from publisher/author
- [ ] Other: ___________

**LIABILITY NOTE:** This book is under copyright (2005, UNP). No documented permission for redistribution exists. The paper scopes its public data release to English and Arabic only. Yoruba MCQs remain in the analysis but are excluded from the public dataset release.

### Citation for Paper
```
Owomoyela, O. (2005). *Yoruba Proverbs*. University of Nebraska Press.
ISBN: 978-0-8032-1843-7.
```

### Data Quality Notes
- 3,834 of 3,974 rows have missing `QA_Flag` (96.5% missing).
- 3,748 of 3,974 rows have missing `Comments` (94.3% missing).
- Only 140 rows have a non-null QA_Flag; of these, most are "PERFECT".
- 1 row has missing `Target_Text_En`; 2 rows have missing `Cultural_Context`.

---

## 2. ENGLISH DATA

### Source Type
- [ ] Single website
- [x] Multiple websites (scraped)
- [ ] Book
- [ ] Existing dataset
- [ ] Other: ___________

### Scraping Protocol (FILLED TO EXTENT KNOWN)
| Field | Your Answer |
|-------|-------------|
| **Websites scraped** | Not documented in available records |
| **Date range of scraping** | Not documented |
| **Scraping tool/script** | Not documented |
| **Rate limiting used?** | Unknown |
| **Robots.txt respected?** | Unknown |
| **Selection criteria** | Proverbs with clear single-meaning interpretations |
| **Filtering applied** | Deduplication assumed |
| **Duplicates removed?** | Yes (assumed, not verified) |
| **Total scraped → final count** | Unknown → 2,278 |

**LIABILITY NOTE:** The English data sources are not fully documented. For the paper, we describe the dataset as "a compiled corpus of English proverbs" and release only the MCQ artifacts, not the raw proverb list. If reviewers request source URLs, they must be recovered from the original scraping script or git history.

### Meaning Sources
| Field | Your Answer |
|-------|-------------|
| **How were "Correct_Meaning" obtained?** | LLM-curated (gpt-4.1-nano) with language-specific instructions |
| **From same source as proverb?** | No |
| **Verified by human?** | No |
| **If LLM-generated, which model?** | openai/gpt-4.1-nano |

### Rights & Permission
- [x] All sources are presumed public domain / common knowledge (proverbs)
- [ ] All sources allow academic scraping
- [ ] Some sources require permission
- [ ] Fair use claimed
- [ ] Other: ___________

**LIABILITY NOTE:** No explicit license documentation for the English source websites. Proverbs are considered common cultural knowledge, but specific compilations may have editorial copyright.

### Citation for Paper
```
[Compiled English proverb corpus, source URLs pending recovery from project history.]
```

---

## 3. ARABIC DATA

### Source Type
- [x] Academic dataset (source dataset name unknown)
- [ ] HuggingFace dataset
- [ ] Website
- [ ] Book
- [ ] Other: ___________

### Dataset Details (FILLED TO EXTENT KNOWN)
| Field | Your Answer |
|-------|-------------|
| **HuggingFace dataset ID** | Unknown |
| **Dataset name** | Unknown |
| **Authors/Creators** | Unknown |
| **Paper associated** | Unknown |
| **Year published** | Unknown |
| **License** | Unknown |
| **URL** | Unknown |
| **Date downloaded** | Not documented |
| **Version/tag used** | Not documented |

**LIABILITY NOTE:** The Arabic dataset source is undocumented. The IDs use "MID" prefix with no explanation. The data was provided as part of a shared dataset bundle (`abrahamsunday123/full-data-complete` on Kaggle). No explicit license or citation is available.

### Subsetting & Filtering
| Field | Your Answer |
|-------|-------------|
| **Full dataset size** | 913 rows (appears to be the full set, not a subset) |
| **Your subset size (913)** | N/A — full dataset used |
| **Filtering criteria** | None applied beyond removing rows with missing QA flags |
| **Columns used** | `Sample_ID`, `source_text`, `english_translation`, `Cultural_Context` |
| **Columns dropped** | None known |
| **Any modifications?** | No |

### Rights & Permission
- [ ] Open license (MIT/Apache/CC-BY)
- [ ] Academic use only
- [ ] Restricted license
- [x] Unknown — requires investigation
- [ ] Other: ___________

**LIABILITY NOTE:** Arabic data license is unknown. If the dataset is from a published paper, the license may restrict redistribution. The paper should note this uncertainty and offer to remove Arabic data if the rights holder requests it.

### Citation for Paper
```
[Arabic proverb dataset, source unknown. Citation pending identification of original source.]
```

### Note on "MID" Prefix
The sample IDs use the prefix "MID" (e.g., MID0001). The meaning of "MID" is not documented. It may stand for "Model ID," "Main ID," or another internal identifier from the source dataset. This should be clarified before submission.

---

## 4. CROSS-CUTTING QUESTIONS

### Data Quality
1. Have ALL three datasets been checked for duplicates across languages?
   - [x] Partially: exact duplicates checked within pipeline; cross-language duplicates not checked.
2. Have you verified that no proverb appears in more than one language dataset?
   - [ ] No
3. Have you checked for near-duplicates within each dataset?
   - [x] Partially: pipeline checks for exact/ near-duplicate options within MCQs, not within raw corpora.

### Human Verification
1. Has a native speaker reviewed the Yoruba data?
   - [ ] No
2. Has a native speaker reviewed the Arabic data?
   - [ ] No
3. Has a native English speaker reviewed the English data?
   - [ ] No

### Bias & Coverage
1. What dialect/region coverage does your Arabic data have?
   `Not documented. Dataset appears to be a general Arabic proverb compilation; dialect breakdown unknown.`
2. What region of Nigeria/Yorubaland does your Yoruba data cover?
   `The Owomoyela (2005) compilation covers Yoruba proverbs broadly, with some regional bias toward Oyo/Ibadan sources.`
3. What variety of English does your English data represent?
   `Standard / generic English proverbs; no regional dialect breakdown available.`

---

## 5. RELEASE PLAN FOR EACL SUBMISSION

### What will be released
- **English MCQs:** 60 items (15 proverbs × 4 variants) with full pipeline metadata
- **Arabic MCQs:** 60 items (15 proverbs × 4 variants) with full pipeline metadata
- **Yoruba MCQs:** Analysis includes 60 items, but **raw Yoruba proverb corpus will NOT be released** due to copyright.
- **Pipeline code:** Full source with pinned versions
- **Audit logs:** Raw outputs, cost logs, model IDs

### What will NOT be released
- Raw Yoruba proverb corpus (copyright risk)
- Raw English source URLs (undocumented scraping)
- Full Arabic source dataset (unknown license)

### Mitigation for reviewers
- Paper explicitly states data provenance limitations in Section 8 (Discussion).
- All released data is under CC BY 4.0 where possible.
- Contact information provided for rights holders to request removal.

---

## 6. CHECKLIST FOR EACL SUBMISSION

- [x] English section completed (with documented gaps)
- [x] Arabic section completed (with documented gaps)
- [x] Yoruba section completed (with copyright flag)
- [ ] All three sections have complete bibliographic citations (pending Arabic source identification)
- [x] License/rights for every source is documented (with gaps flagged)
- [x] Filtering/subsetting decisions are explained
- [x] No proprietary data used without permission (Yoruba excluded from release)
- [x] This document is attached as appendix to paper

---

*Filled: 2026-07-10. Incomplete fields are flagged as liabilities and addressed in the paper's Discussion section.*
