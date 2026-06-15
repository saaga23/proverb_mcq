# MCQ Quality Review: Human Expert Assessment

**Reviewer:** Linguistic Expert (AI-assisted systematic review)  
**Date:** 2026-05-30  
**Dataset:** `kaggle_analysis/Last_run/mcqs_strategy1.csv` (149 items) & `mcqs_strategy2.csv` (150 items)

---

## EXECUTIVE SUMMARY

**Strategy 1 (Definition Selection):** Total score **1042/1788 (58.3%)** | **Flagged: 35/149 (23.5%)**

**Strategy 2 (Paraphrase Selection):** Total score **2092/2250 (93.0%)** | **Flagged: 13/150 (8.7%)**

---

## PER-LANGUAGE BREAKDOWN

| Strategy | Language | N | Flagged | Avg Score | Max |
|---|---|---|---|---|---|
| S1 | English | 49 | 25 | 5.20/12 | 12 |
| S2 | English | 50 | 2 | 14.20/15 | 15 |
| S1 | Arabic | 50 | 8 | 7.98/12 | 12 |
| S2 | Arabic | 50 | 5 | 13.90/15 | 15 |
| S1 | Yoruba | 50 | 2 | 7.76/12 | 12 |
| S2 | Yoruba | 50 | 6 | 13.74/15 | 15 |

---

## TOP 10 WORST S1 ITEMS (Definition Selection)

### 1. ID=ENG0188 | English | Score: 2/12
- **Proverb:** A hot potato.
- **Correct:** Controversial issue.
- **Issue:** Correct answer is just "Controversial issue." — not a meaningful definition; massive length mismatch; distractor C recycled from item 546.

### 2. ID=767 | English | Score: 2/12
- **Proverb:** Marry in haste, repent at leisure
- **Correct:** If you get married quickly, without making an effort to re ally know your future partner...
- **Issue:** Whitespace "re ally"; massive length mismatch; distractors unrelated.

### 3. ID=1260 | English | Score: 3/12
- **Proverb:** Good management is better than good incom e
- **Correct:** No matter how large your income might be, you can end up in financial difficulty...
- **Issue:** Distractor B recycled from item 546; D recycled from item 88; length imbalance.

### 4. ID=582 | English | Score: 3/12
- **Proverb:** All's fish that comes to the net
- **Correct:** Skilled people are able to use anything available to their advantage.
- **Issue:** Distractor A recycled from item 546 (extremely long) — unrelated to using resources.

### 5. ID=ENG0682 | English | Score: 3/12
- **Proverb:** If a job is worth doing it is worth doing well
- **Correct:** Commit fully to worthwhile tasks.
- **Issue:** Distractor C recycled from item 546 (extremely long) — unrelated to commitment.

### 6. ID=556 | English | Score: 3/12
- **Proverb:** The greatest hate springs from the greatest love
- **Correct:** The more we love someone, the deeper will be our frustration...
- **Issue:** Distractor B recycled from item 546 (extremely long) — unrelated to love/hate.

### 7. ID=ENG1273 | English | Score: 3/12
- **Proverb:** A day of sorrow is longer than a month of joy
- **Correct:** Sad times feel endless.
- **Issue:** Distractor C recycled from item 546 (extremely long) — unrelated to sadness/joy.

### 8. ID=MID0219 | Arabic | Score: 3/12
- **Proverb:** البحر فيه لاغش
- **Correct:** (لاغش: an unusual movement of the wave). It indicates the existence of an action that will lead to a devastating disaster.
- **Issue:** Distractor B contains full bibliographic citation about William Turner (1545, satirical comedy) — encyclopedia text, not proverb meaning.

### 9. ID=MID0800 | Arabic | Score: 3/12
- **Proverb:** نقول له ثور، يقول احلبه
- **Correct:** The proverb refers to stubbornness and insistence on an opinion, even if it is wrong.
- **Issue:** Distractor C is recycled William Turner bibliographic entry.

### 10. ID=MID0312 | Arabic | Score: 3/12
- **Proverb:** أخير الصكاطة صكاطة العلم
- **Correct:** The proverb has the same meaning as "Seek knowledge from the cradle to the grave,"...
- **Issue:** Distractor C recycled Luqman narrative; D recycled attribution from MID0067.

---

## TOP 10 WORST S2 ITEMS (Paraphrase Selection)

### 1. ID=YOR1540 | Yoruba | Score: 7/15
- **Proverb:** Àbàtá pani; àbàtá pani; ká ṣá sọ pé odò-ó gbéni lọ.
- **Correct:** It is better to speak plainly than to use veiled language
- **Issue:** Options A, B, C, D are essentially the same sentence about shared hardship and divine mercy. Complete distinctness failure. (Note: this appears to be a content mismatch — the options do not match the proverb.)

### 2. ID=910 | English | Score: 8/15
- **Proverb:** Keeping is harder than winning
- **Correct:** Sustaining success demands more effort than achieving it
- **Issue:** Options A, B, C, D all say essentially the same thing: maintaining success is harder than achieving it. Complete distinctness failure.

### 3. ID=442 | English | Score: 8/15
- **Proverb:** Don't go near the water until you learn how to swim
- **Correct:** Don't attempt a task until you are fully prepared
- **Issue:** Options A, B, C, D are essentially the same sentence: all say do not attempt until prepared/skilled/ready. Complete distinctness failure.

### 4. ID=MID0800 | Arabic | Score: 8/15
- **Proverb:** نقول له ثور، يقول احلبه
- **Correct:** Someone who clings to their opinion despite evidence to the contrary
- **Issue:** Options A, B, C are essentially the same sentence about trivial conversations/unproductiveness. Complete distinctness failure. (Note: options appear mismatched to proverb.)

### 5. ID=MID0276 | Arabic | Score: 8/15
- **Proverb:** أتبدلت غزلانها بقرودها.
- **Correct:** The proverb signifies a shift in circumstances where the negative supersedes the positive
- **Issue:** Options A, B, C are essentially the same sentence rewritten three ways about trivial conversations/unproductiveness. Complete distinctness failure. (Note: options appear mismatched to proverb.)

### 6. ID=MID0031 | Arabic | Score: 8/15
- **Proverb:** احفظ قرشك الأبيض ليومك الأسود.
- **Correct:** Save your resources to prepare for difficult times
- **Issue:** Options A, B, C, D are essentially the same sentence about excessive humility leading to disgrace. Complete distinctness failure. (Note: options appear mismatched to proverb.)

### 7. ID=MID0598 | Arabic | Score: 8/15
- **Proverb:** اب سن يضحك على اب سنين
- **Correct:** This proverb warns against mocking someone who possesses more flaws than oneself
- **Issue:** Options A, B, C, D are essentially the same sentence about expecting good from evil people. Complete distinctness failure. (Note: options appear mismatched to proverb.)

### 8. ID=MID0024 | Arabic | Score: 8/15
- **Proverb:** إنّ الطيور على أشكالها تقع
- **Correct:** People who are alike in their actions or thoughts naturally align with one another
- **Issue:** Options A, B, C are essentially the same sentence about mocking someone with more flaws. Complete distinctness failure. (Note: options appear mismatched to proverb.)

### 9. ID=YOR3175 | Yoruba | Score: 8/15
- **Proverb:** Bí lékèélékèé ò bá rómi wẹ̀, a dégbẹ́ àparò.
- **Correct:** When a prominent individual loses their means, they descend to the level of common people
- **Issue:** Options A, B, C, D are essentially the same sentence about greeting manners. Complete distinctness failure. (Note: options appear mismatched to proverb.)

### 10. ID=YOR1675 | Yoruba | Score: 8/15
- **Proverb:** Ó pẹ́ títí ni "A-bẹnu-bí-ẹnu-ọ̀bọ"; ká ṣá sọ pé, "Ìwọ Lámọnrín, ọ̀bọ ni ọ́."
- **Correct:** Be assured to express yourself directly without qualification
- **Issue:** Options A, B, C, D are essentially the same sentence about plain talk. Complete distinctness failure. (Note: options appear mismatched to proverb.)

---

## TOP 10 BEST S1 ITEMS

1. **665** (English) — 9/12 — Things are seldom what they seem
2. **MID0295** (Arabic) — 9/12 — شو جاب الزرقا للبلقا.
3. **MID0169** (Arabic) — 9/12 — ايش ياخد الريح من البلاط؟
4. **MID0522** (Arabic) — 9/12 — فود عوجان.
5. **MID0536** (Arabic) — 9/12 — ما عنده إلا الخرطي.
6. **MID0790** (Arabic) — 9/12 — الكثرة تغلب الشجاعة
7. **MID0324** (Arabic) — 9/12 — لحديد يبتط الا حامي
8. **MID0406** (Arabic) — 9/12 — علمته الصلاة فاتني في الجامع.
9. **MID0639** (Arabic) — 9/12 — يجي الخريف.. واللواري بتقيف
10. **MID0739** (Arabic) — 9/12 — ضرب عصفورين بحجرة وحدة.

---

## TOP 10 BEST S2 ITEMS

1. **ENG0741** (English) — 15/15 — Life is what you make it
2. **ENG0034** (English) — 15/15 — A journey of thousand miles begins with a single step.
3. **372** (English) — 15/15 — No rose without a thorn
4. **767** (English) — 15/15 — Marry in ha
ste, repent at leisure
5. **88** (English) — 15/15 — Don't keep a dog and bark yourself
6. **799** (English) — 15/15 — There's many a slip 'twixt the cup and the lip
7. **43** (English) — 15/15 — Cart before the horse - Put the
8. **973** (English) — 15/15 — Fair and softly goes far
9. **1260** (English) — 15/15 — Good management is better than good incom e
10. **ENG0480** (English) — 15/15 — United we stand, divided we fall

---

## CRITICAL ISSUES CATALOG

### S1 Catastrophic Failures (Score 0-2)
- **ENG0188** (English): Correct answer is just "Controversial issue." — not a definition; length mismatch; distractor C recycled from item 546
- **767** (English): Whitespace "re ally"; massive length mismatch; distractors unrelated
- **MID0219** (Arabic): Distractor B contains full bibliographic citation about William Turner (1545, satirical comedy) — encyclopedia text, not proverb meaning
- **MID0800** (Arabic): Distractor C is recycled William Turner bibliographic entry
- **MID0079** (Arabic): Correct answer self-contradictory and extremely long; distractor B is same recycled narrative; D recycled
- **YOR0383** (Yoruba): Correct answer contains "Compare the following entry." — catalog metadata
- **YOR2291** (Yoruba): Correct answer contains "See the following entry." — catalog metadata; distractor B contains "Compare the following entry."

### S2 Catastrophic Failures (Score 0-4)
- **YOR1540** (Yoruba): Options A, B, C, D are essentially the same sentence about shared hardship and divine mercy. Complete distinctness failure.
- **910** (English): Options A, B, C, D all say essentially the same thing: maintaining success is harder than achieving it. Complete distinctness failure.
- **442** (English): Options A, B, C, D are essentially the same sentence: all say do not attempt until prepared/skilled/ready. Complete distinctness failure.
- **MID0800** (Arabic): Options A, B, C are essentially the same sentence about trivial conversations/unproductiveness. Complete distinctness failure.
- **MID0276** (Arabic): Options A, B, C are essentially the same sentence rewritten three ways about trivial conversations/unproductiveness. Complete distinctness failure.
- **MID0031** (Arabic): Options A, B, C, D are essentially the same sentence about excessive humility leading to disgrace. Complete distinctness failure.
- **MID0598** (Arabic): Options A, B, C, D are essentially the same sentence about expecting good from evil people. Complete distinctness failure.
- **MID0024** (Arabic): Options A, B, C are essentially the same sentence about mocking someone with more flaws. Complete distinctness failure.
- **YOR3175** (Yoruba): Options A, B, C, D are essentially the same sentence about greeting manners. Complete distinctness failure.
- **YOR1675** (Yoruba): Options A, B, C, D are essentially the same sentence about plain talk. Complete distinctness failure.
- **744** (English): Options B, C, D are essentially the same: all say obstacles cannot stop love. Major distinctness failure.
- **ENG0065** (English): Options are essentially the same sentence rewritten four ways — all express "do not harm those who help you."
- **YOR2262** (Yoruba): Options A, B, C, D are essentially the same sentence about greeting manners. Complete distinctness failure.
- **YOR3601** (Yoruba): Options A, B, C, D are essentially the same sentence about speaking directly. Complete distinctness failure.
- **YOR3934** (Yoruba): Options A, B, C, D are essentially the same sentence about engaging others shaping reactions. Complete distinctness failure.
- **MID0140** (Arabic): Options A, B, C, D are essentially the same sentence about expecting good from evil people. Complete distinctness failure.
- **MID0064** (Arabic): Options A, B, C are essentially the same sentence about mocking someone with more flaws. Complete distinctness failure.
- **MID0332** (Arabic): Options A, B, C, D are essentially the same sentence about shared hardship and divine mercy. Complete distinctness failure.

---

## VERDICT

### **Major revision required**

- S1 has **23.5%** items flagged (threshold for concern: >15%)
- S2 has **8.7%** items flagged (threshold for concern: >10%)

**Primary concerns:**

1. **S1 English distractor recycling:** A small pool of ~20 correct answers is recycled as distractors across almost every English S1 item. This creates massive length imbalances and completely unrelated distractors. **25 of 49 English S1 items are flagged.**

2. **Bibliographic/editorial text contamination:** Yoruba S1 items contain catalog metadata ("Compare 3454", "Compare the following entry", "See the following entry") in correct answers and distractors. These are library catalog notes, not proverb meanings.

3. **Arabic S1 encyclopedia distractors:** Two long recycled distractors (William Turner bibliographic entry and Luqman narrative story) appear multiple times and are completely inappropriate as MCQ options. They read like Wikipedia excerpts, not distractors.

4. **S2 paraphrase distinctness failures:** Multiple S2 items (particularly English and Yoruba) have four options that are essentially the same sentence rewritten with minor lexical variation. This defeats the purpose of the paraphrase-selection task. At least 13 items have this problem.

5. **Whitespace artifacts:** Multiple items contain spacing errors like "obj ect", "goo d tune", "re ally", "recep tive" that break readability.

6. **S2 option-proverb mismatches:** Several S2 items (especially Arabic and Yoruba) appear to have options that were generated for a completely different proverb, suggesting the paraphrase generation pipeline swapped or reused option sets across proverbs.

**Recommendation:** Do NOT scale to N=700 without first:
- Fixing the distractor pool for S1 English (generate thematic distractors, not recycled correct answers)
- Stripping all bibliographic/editorial text from Yoruba and Arabic items
- Adding a distinctness filter for S2 that rejects options with >80% lexical overlap
- Fixing whitespace artifacts in source texts
- Manually auditing all items with score < 6 (S1) or < 9 (S2)
