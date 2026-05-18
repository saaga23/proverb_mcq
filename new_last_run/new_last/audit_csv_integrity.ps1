# audit_csv_integrity.ps1
# Performs deep data integrity audits on the generated CSV files to detect formatting/structural anomalies.

$resultsDir = "c:\Users\User\Downloads\THe proverbeval container\MCQ\new_last_run\new_last"
$genFiles = @(
    @{ Path = "pilot_v5_gen_a_strategy_1.csv"; Task = "A"; Strategy = "Strategy 1" },
    @{ Path = "pilot_v5_gen_a_strategy_2.csv"; Task = "A"; Strategy = "Strategy 2" },
    @{ Path = "pilot_v5_gen_b_strategy_1.csv"; Task = "B"; Strategy = "Strategy 1" },
    @{ Path = "pilot_v5_gen_b_strategy_2.csv"; Task = "B"; Strategy = "Strategy 2" }
)

Write-Output "=========================================================="
Write-Output "       PROVERBGAP MCQ CSV STRUCTURAL INTEGRITY AUDIT      "
Write-Output "==========================================================`n"

foreach ($fileInfo in $genFiles) {
    $filePath = Join-Path $resultsDir $fileInfo.Path
    if (-not (Test-Path $filePath)) {
        Write-Output "[WARNING] File not found: $($fileInfo.Path)"
        continue
    }
    
    $data = Import-Csv -Path $filePath
    $totalRows = $data.Count
    
    $nullFields = 0
    $invalidAnsLabel = 0
    $missingCorrectText = 0
    $duplicateChoices = 0
    $exactDuplicateRows = @{}
    $duplicateRowCount = 0
    
    $rowIdx = 2 # 1-indexed Excel style, header is row 1
    
    foreach ($row in $data) {
        $lang = $row.lang
        if (-not $lang) { $lang = $row.language }
        $sourceProv = $row.source_proverb
        $correctText = $row.correct_text
        $correctAnswerLetter = $row.correct_answer
        if (-not $correctAnswerLetter) { $correctAnswerLetter = $row.Answer }
        
        # Check 1: Empty or null fields
        foreach ($col in @('source_proverb', 'correct_text', 'Choice_A', 'Choice_B', 'Choice_C', 'Choice_D')) {
            if ([string]::IsNullOrWhiteSpace($row.$col)) {
                $nullFields++
                Write-Output "  [Row $rowIdx] EMPTY field '$col' in $lang"
            }
        }
        
        # Check 2: Invalid correct answer label
        if ($correctAnswerLetter -notin @('A', 'B', 'C', 'D')) {
            $invalidAnsLabel++
            Write-Output "  [Row $rowIdx] INVALID correct_answer label: '$correctAnswerLetter' in $lang"
        }
        
        # Check 3: Check if correct_text matches the designated choice exactly
        $designatedChoiceCol = "Choice_$correctAnswerLetter"
        $designatedChoiceText = $row.$designatedChoiceCol
        if ($designatedChoiceText.Trim() -ne $correctText.Trim()) {
            $missingCorrectText++
            Write-Output "  [Row $rowIdx] MISMATCH: designated Choice_$correctAnswerLetter ('$($designatedChoiceText.SubString(0, [Math]::Min(30, $designatedChoiceText.Length)))...') does not match correct_text ('$($correctText.SubString(0, [Math]::Min(30, $correctText.Length)))...')"
        }
        
        # Check 4: Duplicate options in the same row
        $choices = @(
            $row.Choice_A,
            $row.Choice_B,
            $row.Choice_C,
            $row.Choice_D
        )
        
        $uniqueChoices = $choices | Select-Object -Unique
        if ($uniqueChoices.Count -lt 4) {
            $duplicateChoices++
            Write-Output "  [Row $rowIdx] DUPLICATE choices in same question (Unique count: $($uniqueChoices.Count)) for proverb: '$sourceProv'"
            # Print unique choices to see duplicates
            Write-Output "    * A: $($row.Choice_A)"
            Write-Output "    * B: $($row.Choice_B)"
            Write-Output "    * C: $($row.Choice_C)"
            Write-Output "    * D: $($row.Choice_D)"
        }
        
        # Check 5: Duplicate rows (proverbs repeated)
        if ($exactDuplicateRows.ContainsKey($sourceProv)) {
            $duplicateRowCount++
            Write-Output "  [Row $rowIdx] DUPLICATE proverb row: '$sourceProv' previously seen in row $($exactDuplicateRows[$sourceProv])"
        } else {
            $exactDuplicateRows[$sourceProv] = $rowIdx
        }
        
        $rowIdx++
    }
    
    Write-Output ">>> File: $($fileInfo.Path) (Task $($fileInfo.Task) | $($fileInfo.Strategy))"
    Write-Output "  - Total Rows Checked      : $totalRows"
    Write-Output "  - Empty/Null Fields       : $nullFields"
    Write-Output "  - Invalid Answers Label   : $invalidAnsLabel"
    Write-Output "  - Correct Text Mismatches  : $missingCorrectText"
    Write-Output "  - Internal Choice Duplicates: $duplicateChoices"
    Write-Output "  - Duplicate Proverbs (Rows) : $duplicateRowCount"
    Write-Output "`n"
}
