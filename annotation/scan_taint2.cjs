const fs = require('fs')
const file = 'outputs/modal_annotator_log.jsonl'
const lines = fs.readFileSync(file, 'utf8').split('\n').filter(l => l.trim())
let total = 0, cotResponses = 0, nonLetter = 0
const letterRe = /^[A-Da-d]$/
// which field holds the raw response?
let sampleKeys = null
for (const raw of lines) {
  let obj; try { obj = JSON.parse(raw) } catch { continue }
  if (!sampleKeys) sampleKeys = Object.keys(obj)
}
console.log('JSONL fields:', sampleKeys)
const respKeys = sampleKeys.filter(k => /resp|output|completion|text|answer|message/i.test(k))
console.log('candidate response fields:', respKeys)
for (const raw of lines) {
  let obj; try { obj = JSON.parse(raw) } catch { continue }
  total++
  // find the response text
  let resp = ''
  for (const k of respKeys) { if (typeof obj[k] === 'string' && obj[k].length > resp.length) resp = obj[k] }
  const low = resp.toLowerCase()
  if (low.includes('think>') || low.includes('/think>') || low.includes('reasoning:') || low.includes('let me think')) {
    cotResponses++
  }
  const ans = (obj.answer || '').toString().trim()
  if (!letterRe.test(ans)) { nonLetter++; if (nonLetter <= 5) console.log('NON-LETTER answer:', JSON.stringify(obj).slice(0, 200)) }
}
console.log('\ntotal rows:', total)
console.log('responses containing CoT/think markers:', cotResponses)
console.log('non-letter extracted answers:', nonLetter)
