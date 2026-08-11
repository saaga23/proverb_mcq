const fs = require('fs')
const files = [
  'outputs/modal_annotator_log.jsonl',
  'outputs/openrouter_annotator_log.jsonl',
]
const markers = [
  'think>', '/think>', '<reasoning', 'reasoning>', 'Reasoning:',
  'let me think', 'step by step', 'step 1', 'first,', 'option a',
  'i think the answer', 'the correct answer is', 'based on', 'as an ai',
  "i cannot", "i'm sorry", 'sure,', 'here is', 'analysis',
]
for (const file of files) {
  const lines = fs.readFileSync(file, 'utf8').split('\n').filter(l => l.trim())
  let total = 0
  const taint = {}
  const sample = {}
  for (const raw of lines) {
    let obj; try { obj = JSON.parse(raw) } catch { continue }
    total++
    const txt = JSON.stringify(obj).toLowerCase()
    for (const m of markers) {
      if (txt.includes(m.toLowerCase())) {
        taint[m] = (taint[m] || 0) + 1
        if (!sample[m]) sample[m] = JSON.stringify(obj).slice(0, 240)
      }
    }
  }
  console.log('\nFILE:', file, '| lines:', total)
  console.log('taint markers:', JSON.stringify(taint, null, 1))
  if (Object.keys(sample).length) {
    console.log('SAMPLES:')
    for (const k of Object.keys(sample)) console.log('  [' + k + '] ' + sample[k])
  }
}
