import * as fs from 'fs'
import * as path from 'path'
import * as dotenv from 'dotenv'
import https from 'https'

dotenv.config({ path: path.join(__dirname, '..', '.env.local') })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
  console.error('Missing Supabase credentials')
  process.exit(1)
}

interface AnnotationRow {
  annotation_id: string
  item_id: string
  validation_id: string
  language: string
  proverb: string
  option_a: string
  option_b: string
  option_c: string
  option_d: string
  correct_label: string
  gold_meaning: string
  selected_answer: string
  correctness: string
  confidence: string
  time_taken_ms: number
  is_attention_check: boolean
  attention_passed: boolean
  annotator_notes: string
  annotator_id: string
  annotator_nickname: string
  language_expertise: string
  is_native_speaker: string
  age_group: string
  education_level: string
  country: string
  created_at: string
}

function request(path: string, method = 'GET', body: unknown = null): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: new URL(SUPABASE_URL).hostname,
      path,
      method,
      headers: {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
        'Content-Type': 'application/json',
      },
    }
    const req = https.request(options, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data ? JSON.parse(data) : null)
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data.substring(0, 300)}`))
        }
      })
    })
    req.on('error', reject)
    if (body) req.write(JSON.stringify(body))
    req.end()
  })
}

interface RestResponse {
  id: string
  item_id: string
  selected_answer: string
  correctness: string
  confidence: string
  time_taken_ms: number
  is_attention_check: boolean
  attention_passed: boolean
  annotator_notes: string
  annotator_id: string
  created_at: string
  item?: {
    validation_id: string
    language: string
    proverb: string
    option_a: string
    option_b: string
    option_c: string
    option_d: string
    correct_label: string
  }
}

async function exportAnnotations() {
  console.log('Fetching annotations...')

  // Query annotations directly via REST
  const annotationsData = await request('/rest/v1/pg_annotations?select=*&order=created_at.asc', 'GET') as RestResponse[]
  
  if (!annotationsData || annotationsData.length === 0) {
    console.log('No annotations found')
    return
  }

  // Get all unique item_ids
  const itemIds = [...new Set(annotationsData.map(a => a.item_id))]
  
  // Fetch items in batches
  const itemsMap = new Map<string, { validation_id: string; language: string; proverb: string; option_a: string; option_b: string; option_c: string; option_d: string; correct_label: string; gold_meaning?: string }>()
  for (const itemId of itemIds) {
    const item = await request(`/rest/v1/pg_annotation_items?id=eq.${encodeURIComponent(itemId)}&select=*`, 'GET') as Array<{ validation_id: string; language: string; proverb: string; option_a: string; option_b: string; option_c: string; option_d: string; correct_label: string; gold_meaning?: string }>
    if (item && item.length > 0) {
      itemsMap.set(itemId, item[0])
    }
  }

  // Get all unique annotator_ids
  const annotatorIds = [...new Set(annotationsData.map(a => a.annotator_id))]
  
  // Fetch profiles
  interface ProfileRow {
    annotator_id: string
    nickname: string
    language_expertise: string
    is_native_speaker: string
    age_group: string
    education_level: string
    country: string
  }
  const profilesMap = new Map<string, ProfileRow>()
  for (const annotatorId of annotatorIds) {
    const profile = await request(`/rest/v1/pg_annotator_profiles?annotator_id=eq.${encodeURIComponent(annotatorId)}&select=*`, 'GET') as ProfileRow[]
    if (profile && profile.length > 0) {
      profilesMap.set(annotatorId, profile[0])
    }
  }

  // Flatten the data
  const rows: AnnotationRow[] = annotationsData.map(a => {
    const item = itemsMap.get(a.item_id) || { validation_id: '', language: '', proverb: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_label: '', gold_meaning: '' }
    const profile = profilesMap.get(a.annotator_id) || { annotator_id: '', nickname: '', language_expertise: '', is_native_speaker: '', age_group: '', education_level: '', country: '' }
    return {
      annotation_id: a.id,
      item_id: a.item_id,
      validation_id: item.validation_id || '',
      language: item.language || '',
      proverb: item.proverb || '',
      option_a: item.option_a || '',
      option_b: item.option_b || '',
      option_c: item.option_c || '',
      option_d: item.option_d || '',
      correct_label: item.correct_label || '',
      gold_meaning: item.gold_meaning || '',
      selected_answer: a.selected_answer,
      correctness: a.correctness,
      confidence: a.confidence,
      time_taken_ms: a.time_taken_ms,
      is_attention_check: a.is_attention_check,
      attention_passed: a.attention_passed,
      annotator_notes: a.annotator_notes || '',
      annotator_id: a.annotator_id,
      annotator_nickname: profile.nickname || '',
      language_expertise: profile.language_expertise || '',
      is_native_speaker: profile.is_native_speaker || '',
      age_group: profile.age_group || '',
      education_level: profile.education_level || '',
      country: profile.country || '',
      created_at: a.created_at,
    }
  })

  // Write to CSV
  const outputDir = path.join(__dirname, '..', 'output')
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true })
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const outputPath = path.join(outputDir, `annotations_export_${timestamp}.csv`)

  const headers = Object.keys(rows[0])
  const csvContent = [
    headers.join(','),
    ...rows.map(row =>
      headers.map(h => {
        const val = row[h as keyof AnnotationRow]
        if (val === null || val === undefined) return ''
        const str = String(val)
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
          return `"${str.replace(/"/g, '""')}"`
        }
        return str
      }).join(',')
    ),
  ].join('\n')

  fs.writeFileSync(outputPath, csvContent, 'utf-8')
  console.log(`Exported ${rows.length} annotations to: ${outputPath}`)

  // Print summary stats
  const totalAnnotations = rows.length
  const attentionChecks = rows.filter(r => r.is_attention_check)
  const attentionPassed = attentionChecks.filter(r => r.attention_passed)
  const regularAnnotations = rows.filter(r => !r.is_attention_check)

  console.log('\n=== EXPORT SUMMARY ===')
  console.log(`Total annotations: ${totalAnnotations}`)
  console.log(`Regular annotations: ${regularAnnotations.length}`)
  console.log(`Attention checks: ${attentionChecks.length}`)
  console.log(`Attention passed: ${attentionPassed.length}/${attentionChecks.length}`)

  const correctnessCounts = regularAnnotations.reduce((acc, r) => {
    acc[r.correctness] = (acc[r.correctness] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  console.log('\nCorrectness breakdown:')
  Object.entries(correctnessCounts).forEach(([key, count]) => {
    console.log(`  ${key}: ${count} (${(count / regularAnnotations.length * 100).toFixed(1)}%)`)
  })

  const confidenceCounts = regularAnnotations.reduce((acc: Record<string, number>, r) => {
    acc[r.confidence] = (acc[r.confidence] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  console.log('\nConfidence breakdown:')
  Object.entries(confidenceCounts).forEach(([key, count]) => {
    console.log(`  ${key}: ${count} (${(count / regularAnnotations.length * 100).toFixed(1)}%)`)
  })

  const agreementCount = regularAnnotations.filter(r => r.selected_answer === r.correct_label).length
  console.log(`\nAgreement with gold: ${agreementCount}/${regularAnnotations.length} (${(agreementCount / regularAnnotations.length * 100).toFixed(1)}%)`)
}

exportAnnotations().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})
