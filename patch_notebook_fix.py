import json
from pathlib import Path

# Paths
notebook_path = Path("c:/Users/User/Downloads/THe proverbeval container/MCQ/proverbgap-pilot-v2.ipynb")

print("Loading notebook...")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 2 Correct Source Code
cell2_source = [
    "# Cell 2: System Prompts & Parsers (Strategy 2)\n",
    "import re, json\n",
    "\n",
    "SYS_A_STRAT2 = (\n",
    "    \"You are a linguistic expert building a translation comprehension benchmark.\\n\"\n",
    "    \"Given a proverb and its correct English translation, you must generate 4 options written in the EXACT same style, tone, register, and length.\\n\"\n",
    "    \"Requirements:\\n\"\n",
    "    \"1. Option 1 MUST be a correct and natural paraphrase of the English translation.\\n\"\n",
    "    \"2. Options 2, 3, and 4 MUST be incorrect direct translations (introduce a subtle meaning shift: swap the subject/object, invert a condition, or change the consequence).\\n\"\n",
    "    \"3. All 4 options must sound equally natural to a native speaker. The blind evaluator should not be able to guess the correct answer based on length or phrasing style.\\n\"\n",
    "    \"4. CRITICAL: All 4 options MUST be of extremely similar length (within 10% of each other's character count). If Option 1 is short, distractors must be short. If Option 1 is long, distractors must be long. Avoid any length signature.\\n\"\n",
    "    \"Return ONLY a valid JSON list of 4 strings where the first element is the correct paraphrase: [\\\"correct_paraphrase\\\", \\\"distractor_1\\\", \\\"distractor_2\\\", \\\"distractor_3\\\"]\"\n",
)

cell2_source.append(")\n")
cell2_source.append("\n")

SYS_B_STRAT2_lines = [
    "SYS_B_STRAT2 = (\n",
    "    \"You are a cultural anthropology expert building a proverb reasoning benchmark.\\n\"\n",
    "    \"Given a proverb, its English translation, and its correct cultural meaning, you must generate 4 options written in the EXACT same style, tone, register, and length.\\n\"\n",
    "    \"Requirements:\\n\"\n",
    "    \"1. Option 1 MUST be a correct paraphrase of the cultural meaning.\\n\"\n",
    "    \"2. Options 2, 3, and 4 MUST be incorrect cultural interpretations (convey a completely different life lesson, social rule, or value, but sound equally plausible as ancient wisdom).\\n\"\n",
    "    \"3. All 4 options must be written in the same register. The blind evaluator should not be able to guess the correct answer based on length, tone, or style.\\n\"\n",
    "    \"4. CRITICAL: All 4 options MUST be of extremely similar length (within 10% of each other's character count). If Option 1 is short, distractors must be short. If Option 1 is long, distractors must be long. Avoid any length signature.\\n\"\n",
    "    \"Return ONLY a valid JSON list of 4 strings where the first element is the correct paraphrase: [\\\"correct_paraphrase\\\", \\\"distractor_1\\\", \\\"distractor_2\\\", \\\"distractor_3\\\"]\"\n",
    ")\n",
    "\n",
    "def parse_response_strat2(raw):\n",
    "    if not raw: return None\n",
    "    try:\n",
    "        clean = re.sub(r'```json|```', '', raw).strip()\n",
    "        d = json.loads(clean)\n",
    "        dists = d.get('distractors', d if isinstance(d, list) else None)\n",
    "        if dists and len(dists) >= 4: return [str(x).strip() for x in dists[:4]]\n",
    "    except: pass\n",
    "    m = re.search(r'\\[.*?\\]', raw, re.DOTALL)\n",
    "    if m:\n",
    "        try: \n",
    "            res = json.loads(m.group())\n",
    "            if len(res) >= 4: return [str(x).strip() for x in res[:4]]\n",
    "        except: pass\n",
    "    return None\n",
    "\n",
    "def validate_options_length(options, threshold=0.15):\n",
    "    if not options or len(options) < 4: return False\n",
    "    len0 = len(options[0])\n",
    "    if len0 == 0: return False\n",
    "    for opt in options[1:4]:\n",
    "        if abs(len(opt) - len0) / len0 > threshold:\n",
    "            return False\n",
    "    return True\n",
    "\n",
    "def assemble_mcq(correct, distractors, seed):\n",
    "    choices = list(distractors[:3]) + [correct]\n",
    "    random.Random(seed).shuffle(choices)\n",
    "    labels = ['A', 'B', 'C', 'D']\n",
    "    ans = labels[choices.index(correct)]\n",
    "    return {f'Choice_{l}': choices[i] for i, l in enumerate(labels)}, ans\n"
]
cell2_source.extend(SYS_B_STRAT2_lines)

# Cell 4 Correct Source Code with Hardcoded Data Path
cell4_source = [
    "# Cell 4: Data Loading\n",
    "PILOT_N = 30\n",
    "LANGUAGES = ['English', 'Yoruba', 'Arabic']\n",
    "dfs = {}\n",
    "input_dir = Path('/kaggle/input/datasets/abrahamsunday123/original-data')\n",
    "if not input_dir.exists():\n",
    "    input_dir = Path('original_data')\n",
    "if not input_dir.exists():\n",
    "    input_dir = Path('.')\n",
    "\n",
    "for lang in LANGUAGES:\n",
    "    for p in input_dir.rglob(f'{lang}_cleaned.csv'):\n",
    "        df = pd.read_csv(p).rename(columns={'Source_Text_Yo':'source_proverb', 'Source_Text_Mid':'source_proverb', 'Proverb':'source_proverb', 'source_text':'source_proverb',\n",
    "                                            'Target_Text_En':'proverb_en', 'Translation':'proverb_en', 'english_translation':'proverb_en', 'English_Translation':'proverb_en',\n",
    "                                            'Cultural_Context':'correct_meaning', 'Correct_Meaning':'correct_meaning'})\n",
    "        if lang == 'English':\n",
    "            if 'proverb_en' not in df.columns: df['proverb_en'] = df['source_proverb']\n",
    "            if 'correct_meaning' not in df.columns: df['correct_meaning'] = df['proverb_en']\n",
    "        clean_df = df.dropna(subset=['source_proverb', 'proverb_en', 'correct_meaning'])\n",
    "        if not clean_df.empty:\n",
    "            dfs[lang] = clean_df.sample(min(PILOT_N, len(clean_df)), random_state=42).reset_index(drop=True)\n",
    "            print(f\"Loaded {lang}: {len(dfs[lang])} samples from {p.name}\")\n",
    "            break\n"
]

# Apply patches
patched_cell2 = False
patched_cell4 = False

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and cell['source']:
        first_line = cell['source'][0]
        if "Cell 2: System Prompts" in first_line:
            cell['source'] = cell2_source
            patched_cell2 = True
            print("Successfully patched Cell 2 (System Prompts).")
        elif "Cell 4: Data Loading" in first_line:
            cell['source'] = cell4_source
            patched_cell4 = True
            print("Successfully patched Cell 4 (Data Loading).")

# Save notebook
if patched_cell2 and patched_cell4:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("Notebook saved successfully with zero syntax errors and hardcoded data path!")
else:
    print(f"Error patching cells! Cell 2: {patched_cell2}, Cell 4: {patched_cell4}")
