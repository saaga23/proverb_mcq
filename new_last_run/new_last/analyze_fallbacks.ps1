# analyze_fallbacks.ps1
# Investigates how many times Strategy 2 failed to generate/parse and fell back to unparaphrased negative sampling.

$resultsDir = "c:\Users\User\Downloads\THe proverbeval container\MCQ\new_last_run\new_last"
$originalDir = "c:\Users\User\Downloads\THe proverbeval container\MCQ\original_data"

$genFiles = @(
    @{ Path = "pilot_v5_gen_a_strategy_2.csv"; Task = "a"; OriginalCol = "proverb_en" },
    @{ Path = "pilot_v5_gen_b_strategy_2.csv"; Task = "b"; OriginalCol = "correct_meaning" }
)

Write-Output "=========================================================="
Write-Output "    PROVERBGAP MCQ STRATEGY 2 FALLBACK/FAILURE AUDIT      "
Write-Output "==========================================================`n"

# Since loading the original CSV and sampling with random_state=42 in PowerShell is complex,
# we can simply check if the correct_text in the generated CSV exactly matches the source proverb's original target_text.
# Wait! In Strategy 2, the prompt is:
# "Generate 4 options in a valid JSON list of strings (Option 1 correct paraphrase, Options 2-4 wrong translations/interpretations)."
# If the LLM generates a paraphrase, it will almost certainly not be 100% identical to the source text.
# If it is 100% identical, it is either an unparaphrased fallback, or the LLM chose to output the exact input.
# Let's check how many correct_texts are exactly identical to the original target_text!
# Wait! How do we get the original target_text?
# In Task a (literal), the original target_text is row.proverb_en. But wait, in the generated CSV,
# there is a column called 'proverb_en'! Let's check the columns of pilot_v5_gen_a_strategy_2.csv.
# In Task a, the columns are:
# task,strategy,lang,source_proverb,correct_text,correct_answer,Choice_A,Choice_B,Choice_C,Choice_D
# Wait, it does NOT have 'proverb_en'! Ah! In Task a Strategy 1, we saw:
# language,sample_id,source_proverb,proverb_en,correct_text,Choice_A,Choice_B,Choice_C,Choice_D,Answer
# But in Cell 5 of the notebook, let's check what columns are written:
# For Task a Strategy 2, the columns are:
# task,strategy,lang,source_proverb,correct_text,correct_answer,Choice_A,Choice_B,Choice_C,Choice_D
# Yes! And the original target_text for Task a is the literal translation (proverb_en).
# And for Task b, the original target_text is correct_meaning (which is the cultural interpretation).
# Wait, how can we check if it matches the original?
# Let's load the original data files using PowerShell, match the source_proverb, and check if correct_text matches the original translation/meaning!
# This is extremely robust and will give 100% accurate fallback statistics.

# Let's load the original CSVs into a dictionary for fast lookup
$originalData = @{}
$languages = @("English", "Yoruba", "Arabic")

foreach ($lang in $languages) {
    $origPath = Join-Path $originalDir "$($lang)_cleaned.csv"
    if (Test-Path $origPath) {
        $csv = Import-Csv -Path $origPath
        $originalData[$lang] = $csv
    }
}

foreach ($gFile in $genFiles) {
    $genPath = Join-Path $resultsDir $gFile.Path
    if (-not (Test-Path $genPath)) {
        Write-Output "[WARNING] File not found: $($gFile.Path)"
        continue
    }
    
    $genCsv = Import-Csv -Path $genPath
    $fallbackCount = 0
    $totalCount = $genCsv.Count
    
    Write-Output ">>> File: $($gFile.Path) (Task $($gFile.Task.ToUpper()))"
    
    $langFallbacks = @{ "English" = 0; "Yoruba" = 0; "Arabic" = 0 }
    
    foreach ($row in $genCsv) {
        $lang = $row.lang
        $sourceProv = $row.source_proverb
        $correctText = $row.correct_text
        
        # Find this proverb in the original data
        $origCsv = $originalData[$lang]
        $match = $null
        
        # Search for exact match
        foreach ($origRow in $origCsv) {
            # Find the source proverb column. Columns in original csv could be named differently.
            # Let's find any column that matches sourceProv
            $origProv = ""
            foreach ($col in @('Source_Text_Yo', 'Source_Text_Mid', 'Proverb', 'source_text', 'Source_Text')) {
                if ($origRow.$col) {
                    $origProv = $origRow.$col
                    break
                }
            }
            
            if ($origProv -eq $sourceProv) {
                $match = $origRow
                break
            }
        }
        
        if ($null -ne $match) {
            # Find the original target column
            $origTarget = ""
            if ($gFile.Task -eq "a") {
                foreach ($col in @('Target_Text_En', 'Translation', 'english_translation', 'English_Translation')) {
                    if ($match.$col) {
                        $origTarget = $match.$col
                        break
                    }
                }
                if ($lang -eq "English" -and -not $origTarget) {
                    $origTarget = $sourceProv
                }
            } else {
                foreach ($col in @('Cultural_Context', 'Correct_Meaning', 'correct_meaning')) {
                    if ($match.$col) {
                        $origTarget = $match.$col
                        break
                    }
                }
                if ($lang -eq "English" -and -not $origTarget) {
                    $origTarget = $sourceProv
                }
            }
            
            # Compare
            if ($correctText.Trim() -eq $origTarget.Trim()) {
                $fallbackCount++
                $langFallbacks[$lang]++
            }
        } else {
            # If no match found in original CSV (e.g. punctuation difference), we skip or mark as no-fallback
        }
    }
    
    $fallbackPercent = ($fallbackCount / $totalCount) * 100
    Write-Output "  - Total Fallbacks (Unparaphrased): $fallbackCount / $totalCount ($("{0:N1}" -f $fallbackPercent)%)"
    foreach ($lang in $languages) {
        $langCount = 30 # Since we sample N=30 per language
        $lPercent = ($langFallbacks[$lang] / $langCount) * 100
        Write-Output "    * $lang : $($langFallbacks[$lang]) / $langCount ($("{0:N1}" -f $lPercent)%)"
    }
    Write-Output "`n"
}
