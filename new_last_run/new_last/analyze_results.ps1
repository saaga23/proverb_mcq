$dir = "c:\Users\User\Downloads\THe proverbeval container\MCQ\new_last_run\new_last"

# --- HELPER: Read CSV Safely ---
function Get-CSVData($path) {
    if (Test-Path $path) {
        return Import-Csv $path
    }
    return $null
}

# --- ANALYZE SRS (Shortcut Resistance Score) ---
Write-Host "=== SHORTCUT RESISTANCE SCORE (SRS) FORENSIC REPORT ==="
$audit_files = @{
    "A-Strategy 1" = "$dir\pilot_v5_audit_a_strategy_1.csv";
    "A-Strategy 2" = "$dir\pilot_v5_audit_a_strategy_2.csv";
    "B-Strategy 1" = "$dir\pilot_v5_audit_b_strategy_1.csv"
}

foreach ($key in $audit_files.Keys) {
    $path = $audit_files[$key]
    $data = Get-CSVData $path
    if ($data) {
        Write-Host "`n[$key] Summary:"
        $langs = $data | Select-Object -ExpandProperty lang -Unique
        foreach ($l in $langs) {
            $sub = $data | Where-Object { $_.lang -eq $l }
            $correct = $sub | Where-Object { [int]$_.hit_consensus -eq 1 }
            $acc = ($correct.Count / $sub.Count) * 100
            $status = if ($acc -lt 40.0) { "PASS" } elseif ($acc -lt 55.0) { "REVIEW" } else { "FAIL" }
            Write-Host "  - $($l): Acc = $($acc.ToString('F1'))% ($($correct.Count)/$($sub.Count)) [$status]"
        }
        $overall_correct = $data | Where-Object { [int]$_.hit_consensus -eq 1 }
        $overall_acc = ($overall_correct.Count / $data.Count) * 100
        Write-Host "  - OVERALL: $($overall_acc.ToString('F1'))% ($($overall_correct.Count)/$($data.Count))"
    } else {
        Write-Host "`n[$key] - CSV not found or empty."
    }
}

# --- ANALYZE OPTION LENGTH BIAS ---
Write-Host "`n======================================================="
Write-Host "=== OPTION LENGTH Forensics (Strategy 1 vs Strategy 2) ==="
Write-Host "======================================================="

$gen_files = @{
    "Gen A (Strategy 1)" = "$dir\pilot_v5_gen_a_strategy_1.csv";
    "Gen A (Strategy 2)" = "$dir\pilot_v5_gen_a_strategy_2.csv";
    "Gen B (Strategy 1)" = "$dir\pilot_v5_gen_b_strategy_1.csv";
    "Gen B (Strategy 2)" = "$dir\pilot_v5_gen_b_strategy_2.csv"
}

foreach ($key in $gen_files.Keys) {
    $path = $gen_files[$key]
    $data = Get-CSVData $path
    if ($data) {
        Write-Host "`n[$key] Statistics:"
        $total_items = $data.Count
        $total_std_dev = 0
        $correct_longer_count = 0
        $correct_shorter_count = 0
        $total_len_diff = 0

        foreach ($row in $data) {
            # Standardize Choices
            $ca = $row.Choice_A
            $cb = $row.Choice_B
            $cc = $row.Choice_C
            $cd = $row.Choice_D
            $ans = $row.correct_answer

            $l_a = if ($ca) { $ca.Length } else { 0 }
            $l_b = if ($cb) { $cb.Length } else { 0 }
            $l_c = if ($cc) { $cc.Length } else { 0 }
            $l_d = if ($cd) { $cd.Length } else { 0 }
            $lengths = @($l_a, $l_b, $l_c, $l_d)

            # Calculate Mean
            $mean = ($l_a + $l_b + $l_c + $l_d) / 4

            # Calculate Standard Deviation
            $sum_sq = 0
            foreach ($l in $lengths) {
                $sum_sq += [Math]::Pow($l - $mean, 2)
            }
            $std_dev = [Math]::Sqrt($sum_sq / 4)
            $total_std_dev += $std_dev

            # Length of correct option vs average of distractors
            $correct_len = switch ($ans) {
                'A' { $l_a }
                'B' { $l_b }
                'C' { $l_c }
                'D' { $l_d }
            }
            $distractor_len = ($l_a + $l_b + $l_c + $l_d - $correct_len) / 3
            $len_diff = $correct_len - $distractor_len
            $total_len_diff += $len_diff

            if ($correct_len -gt $distractor_len) { $correct_longer_count++ }
            if ($correct_len -lt $distractor_len) { $correct_shorter_count++ }
        }

        $avg_std_dev = $total_std_dev / $total_items
        $avg_len_diff = $total_len_diff / $total_items
        $pct_longer = ($correct_longer_count / $total_items) * 100

        Write-Host "  - Total Items: $total_items"
        Write-Host "  - Average Option Length Std Dev: $($avg_std_dev.ToString('F2')) chars"
        Write-Host "  - Average Length Difference (Correct - Distractors): $($avg_len_diff.ToString('F2')) chars"
        Write-Host "  - Correct Answer is Longer than Distractors in: $($pct_longer.ToString('F1'))% of questions (Expected: 50%)"
    } else {
        Write-Host "`n[$key] - CSV not found or empty."
    }
}
