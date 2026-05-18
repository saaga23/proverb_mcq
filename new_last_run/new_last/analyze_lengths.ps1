# analyze_lengths.ps1
# Analyzes the character lengths of correct options vs distractors to detect leakage/shortcuts.

$resultsDir = "c:\Users\User\Downloads\THe proverbeval container\MCQ\new_last_run\new_last"
$genFiles = @(
    @{ Path = "pilot_v5_gen_a_strategy_1.csv"; Task = "A"; Strategy = "Strategy 1" },
    @{ Path = "pilot_v5_gen_a_strategy_2.csv"; Task = "A"; Strategy = "Strategy 2" },
    @{ Path = "pilot_v5_gen_b_strategy_1.csv"; Task = "B"; Strategy = "Strategy 1" },
    @{ Path = "pilot_v5_gen_b_strategy_2.csv"; Task = "B"; Strategy = "Strategy 2" }
)

Write-Output "=========================================================="
Write-Output "       PROVERBGAP MCQ OPTION LENGTH LEAKAGE AUDIT         "
Write-Output "==========================================================`n"

foreach ($fileInfo in $genFiles) {
    $filePath = Join-Path $resultsDir $fileInfo.Path
    if (-not (Test-Path $filePath)) {
        Write-Output "[WARNING] File not found: $($fileInfo.Path)"
        continue
    }
    
    # We load CSV using Import-Csv. Since some files have newlines within fields (like Arabic strings), 
    # we use Import-Csv which handles quoted fields with newlines correctly in PowerShell!
    $data = Import-Csv -Path $filePath
    
    $totalCorrectLen = 0
    $totalDistLen = 0
    $distCount = 0
    $itemCount = $data.Count
    
    # We will track metrics per language too
    $langStats = @{}
    
    foreach ($row in $data) {
        $lang = $row.lang
        if (-not $langStats.Contains($lang)) {
            $langStats[$lang] = @{ CorrectLen = 0; DistLen = 0; Count = 0 }
        }
        
        $correctAnswerLetter = $row.correct_answer
        $correctText = ""
        $distractors = @()
        
        # Identify correct vs distractor choices
        foreach ($letter in @('A', 'B', 'C', 'D')) {
            $choiceVal = $row."Choice_$letter"
            if ($null -eq $choiceVal) { continue }
            
            if ($letter -eq $correctAnswerLetter) {
                $correctText = $choiceVal
            } else {
                $distractors += $choiceVal
            }
        }
        
        $cLen = $correctText.Length
        $totalCorrectLen += $cLen
        $langStats[$lang].CorrectLen += $cLen
        
        foreach ($d in $distractors) {
            $dLen = $d.Length
            $totalDistLen += $dLen
            $distCount++
            $langStats[$lang].DistLen += $dLen
        }
        
        $langStats[$lang].Count++
    }
    
    $avgCorrect = $totalCorrectLen / $itemCount
    $avgDist = $totalDistLen / $distCount
    $diff = $avgCorrect - $avgDist
    
    Write-Output ">>> Task: $($fileInfo.Task) | Strategy: $($fileInfo.Strategy) ($($fileInfo.Path))"
    Write-Output "Total Samples: $itemCount"
    Write-Output "Overall Average Lengths:"
    Write-Output "  - Correct Option   : $("$("{0:N1}" -f $avgCorrect)") chars"
    Write-Output "  - Distractor Option: $("$("{0:N1}" -f $avgDist)") chars"
    Write-Output "  - Delta (Correct - Dist): $("$("{0:N1}" -f $diff)") chars"
    
    Write-Output "Per-Language Deltas:"
    foreach ($lang in $langStats.Keys) {
        $lCount = $langStats[$lang].Count
        if ($lCount -gt 0) {
            $lAvgC = $langStats[$lang].CorrectLen / $lCount
            $lAvgD = $langStats[$lang].DistLen / ($lCount * 3)
            $lDiff = $lAvgC - $lAvgD
            Write-Output "  - $lang : Correct=$("{0:N1}" -f $lAvgC) | Dist=$("{0:N1}" -f $lAvgD) | Delta=$("{0:N1}" -f $lDiff) chars"
        }
    }
    Write-Output "`n"
}
