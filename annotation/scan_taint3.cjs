const fs = require('fs')
const path = require('path')

// 1) Inspect answer column of the FINAL IAA source CSVs
const csvs = [
  'outputs/modal_annotation_results_modal_annotator_20260708_111745.csv',
  'outputs/openrouter_annotation_results_openrouter_annotator_20260707_212031.csv',
]
const letterRe = /^[A-Da-d]$/
for (const c of csvs) {
  const rows = fs.readFileSync(c, 'utf8').trim().split('\n')
  const header = rows[0].split(',')
  const ai = header.indexOf('answer')
  const bad = []
  for (let i = 1; i < rows.length; i++) {
    const cols = rows[i].split(',')
    const ans = (cols[ai] || '').trim()
    if (!letterRe.test(ans)) bad.push(rows[i].slice(0, 80))
  }
  console.log('\nCSV:', c)
  console.log('  rows:', rows.length - 1, '| non-letter answers:', bad.length)
  if (bad.length) console.log('  examples:', bad.slice(0, 5))
}

// 2) Re-run the production extractor logic on a DeepSeek-R1 think response
function extractAnswer(resp) {
  const letters = (resp || '').match(/[ABCD]/g)
  if (!letters || letters.length === 0) return null
  return letters[letters.length - 1] // last standalone occurrence (handles CoT)
}
const log = fs.readFileSync('outputs/modal_annotator_log.jsonl', 'utf8').split('\n').filter(l => l.trim())
let shown = 0
for (const raw of log) {
  let o; try { o = JSON.parse(raw) } catch { continue }
  if (o.model && o.model.includes('DeepSeek-R1') && o.response && o.response.toLowerCase().includes('think>')) {
    const ans = extractAnswer(o.response)
    console.log('\nDeepSeek-R1 ' + o.validation_id + ' extracted answer:', ans)
    console.log('  response tail:', o.response.slice(-300).replace(/\n/g, ' '))
    shown++; if (shown >= 3) break
  }
}
