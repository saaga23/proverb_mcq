# Data Provenance Documentation Template

> **Purpose**: EACL reviewers will scrutinize data sources. This document must be complete, accurate, and cite every source. Fill in ALL blanks below.

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
| **Proverbs extracted** | ~3,931 (subset) |
| **Pages used** | Full book (OCR'd in 7 parts) |
| **Library/Archive** | Personal copy / acquired PDF |

### OCR Process
| Field | Your Answer |
|-------|-------------|
| **OCR tool** | `________________________________` |
| **Date of OCR** | `________________________________` |
| **Post-processing** | `________________________________` |
| **Error rate estimate** | `________________________________` |

### Rights & Permission
- [ ] Book is in public domain
- [ ] Book is out of copyright (published before _____)
- [ ] Fair use / academic use permitted
- [ ] Permission obtained from publisher/author
- [ ] Other: ___________

### Citation for Paper
```
Owomoyela, O. (2005). *Yoruba Proverbs*. University of Nebraska Press.
ISBN: 978-0-8032-1843-7.
```

### Note on Oral Tradition
Yoruba proverbs are part of oral tradition. The book compiled them. The proverbs themselves are traditional knowledge; the English translations and explanations are the author's work. Cite the compilation.

---

## 2. ENGLISH DATA

### Source Type
- [ ] Single website
- [x] Multiple websites (scraped)
- [ ] Book
- [ ] Existing dataset
- [ ] Other: ___________

### Scraping Protocol (REQUIRED)
| Field | Your Answer |
|-------|-------------|
| **Websites scraped** | List ALL: `____________________________` |
| **Date range of scraping** | `________________________________` |
| **Scraping tool/script** | `________________________________` |
| **Rate limiting used?** | `________________________________` |
| **Robots.txt respected?** | `________________________________` |
| **Selection criteria** | `________________________________` |
| **Filtering applied** | `________________________________` |
| **Duplicates removed?** | `________________________________` |
| **Total scraped → final count** | `________ → ________` |

### Meaning Sources
| Field | Your Answer |
|-------|-------------|
| **How were "Correct_Meaning" obtained?** | `____________________________` |
| **From same source as proverb?** | `____________________________` |
| **Verified by human?** | `____________________________` |
| **If LLM-generated, which model?** | `____________________________` |

### Rights & Permission
- [ ] All sources are public domain
- [ ] All sources allow academic scraping
- [ ] Some sources require permission
- [ ] Fair use claimed
- [ ] Other: ___________

### Citation for Paper
```
[Your citation here. If multiple web sources, list them or cite a compilation.]
```

---

## 3. ARABIC DATA

### Source Type
- [ ] HuggingFace dataset
- [ ] Academic dataset
- [ ] Website
- [ ] Book
- [ ] Other: ___________

### Dataset Details (REQUIRED)
| Field | Your Answer |
|-------|-------------|
| **HuggingFace dataset ID** | `________________________________` |
| **Dataset name** | `________________________________` |
| **Authors/Creators** | `________________________________` |
| **Paper associated** | `________________________________` |
| **Year published** | `________________________________` |
| **License** | `________________________________` |
| **URL** | `________________________________` |
| **Date downloaded** | `________________________________` |
| **Version/tag used** | `________________________________` |

### Subsetting & Filtering
| Field | Your Answer |
|-------|-------------|
| **Full dataset size** | `________________________________` |
| **Your subset size (913)** | Why this number? `________________` |
| **Filtering criteria** | `________________________________` |
| **Columns used** | `source_text, english_translation, Cultural_Context` |
| **Columns dropped** | `________________________________` |
| **Any modifications?** | `________________________________` |

### Rights & Permission
- [ ] Open license (MIT/Apache/CC-BY)
- [ ] Academic use only
- [ ] Restricted license
- [ ] Other: ___________

### Citation for Paper
```
[Your citation here. Must match the dataset's requested citation format.]
```

### Note on "MID" Prefix
Your sample IDs use "MID0001", "MID0002"... What does "MID" stand for?
`________________________________`

---

## 4. CROSS-CUTTING QUESTIONS

### Data Quality
1. Have ALL three datasets been checked for duplicates across languages?
   - [ ] Yes
   - [ ] No
   - [ ] Partially

2. Have you verified that no proverb appears in more than one language dataset?
   - [ ] Yes
   - [ ] No

3. Have you checked for near-duplicates within each dataset?
   - [ ] Yes
   - [ ] No

### Human Verification
1. Has a native speaker reviewed the Yoruba data?
   - [ ] Yes (name: `________`)
   - [ ] No

2. Has a native speaker reviewed the Arabic data?
   - [ ] Yes (name: `________`)
   - [ ] No

3. Has a native English speaker reviewed the English data?
   - [ ] Yes (name: `________`)
   - [ ] No

### Bias & Coverage
1. What dialect/region coverage does your Arabic data have?
   `________________________________`

2. What region of Nigeria/Yorubaland does your Yoruba data cover?
   `________________________________`

3. What variety of English does your English data represent?
   `________________________________`

---

## 5. CHECKLIST FOR EACL SUBMISSION

- [ ] All three sections above are COMPLETELY filled in
- [ ] Every source has a bibliographic citation
- [ ] License/rights for every source is documented
- [ ] Filtering/subsetting decisions are explained
- [ ] No proprietary data used without permission
- [ ] This document is attached as appendix to paper

---

## 6. NATIVE SPEAKER RECRUITMENT GUIDE

### Where to Find Native Speakers

**Arabic speakers:**
- Upwork: Search "Arabic linguist" or "Arabic translator" (~$15-25/hr)
- Fiverr: Search "Arabic proofreading" (~$10-20/task)
- ProZ.com: Professional translator network
- Your university's Arabic department / Middle Eastern Studies
- r/arabs, r/learn_arabic on Reddit (academic volunteer appeal)
- Twitter/X: #Arabic #linguistics community

**Yoruba speakers:**
- Upwork: "Yoruba translator" (~$15-30/hr)
- Fiverr: "Yoruba proofreading"
- University of Ibadan / Obafemi Awolowo University (reach out to Linguistics dept)
- Nigerian diaspora communities (LinkedIn, Facebook groups)
- ProZ.com

**English speakers:**
- Easiest to find — any native English speaker with linguistics background
- Your own department
- r/linguistics, r/AskLinguistics

### Validation Protocol (Minimal Viable)

**Per language:**
- **2 native speakers** (minimum for inter-annotator agreement)
- **50 items each** (~2-3 hours work)
- **Tasks:**
  1. Is the proverb text correct? (typo check)
  2. Is the meaning explanation accurate?
  3. Is the S2-generated distractor plausible but clearly wrong?
  4. Would a native speaker recognize this proverb?

**Payment:**
- ~$50-75 per speaker per language
- Total: ~$300-450 for all three languages

**Documentation for paper:**
- "Two native speaker validators per language reviewed 50 randomly sampled items for correctness, cultural appropriateness, and distractor quality. Inter-annotator agreement was calculated."

### Quick Start Action

1. **Today**: Post on Upwork/Fiverr for Arabic and Yoruba validators
2. **This week**: Email your university's relevant departments
3. **Within 2 weeks**: Select validators, send them the 50-item samples
4. **Within 4 weeks**: Collect feedback, incorporate corrections
5. **Document everything**: Save screenshots, emails, payment receipts

---

*Fill in this template completely. Incomplete provenance = desk reject at EACL.*
