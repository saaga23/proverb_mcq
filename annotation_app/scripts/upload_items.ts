import * as fs from 'fs'
import * as path from 'path'
import * as dotenv from 'dotenv'
import https from 'https'
import { parse } from 'csv-parse/sync'

dotenv.config({ path: path.join(__dirname, '..', '.env.local') })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
  console.error('Missing Supabase credentials')
  process.exit(1)
}

interface CsvRow {
  generator_model: string
  variant: string
  mcq_id: string
  language: string
  sample_id: string
  proverb: string
  correct_meaning: string
  original_meaning: string
  curated_meaning: string
  correct_label: string
  option_A: string
  option_B: string
  option_C: string
  option_D: string
  generation_status: string
  fallback_count: string
  length_replaced: string
  leak_replaced: string
  nli_replaced: string
  duplicate_options: string
  consensus_label: string
  consensus_frac: string
  consensus_correct: string
  validation_id: string
}

function parseCsv(content: string): CsvRow[] {
  const records = parse(content, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
  })
  return records as CsvRow[]
}

function request(path: string, method = 'GET', body: unknown = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: new URL(SUPABASE_URL).hostname,
      path,
      method,
      headers: {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=representation',
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

async function uploadItems() {
  const csvPath = path.join(__dirname, '..', '..', 'data', 'production', 'paper_first_outputs_2026-06-22_10-42-02', 'human_validation_sample_60.csv')
  if (!fs.existsSync(csvPath)) {
    console.error(`CSV not found: ${csvPath}`)
    process.exit(1)
  }

  const csvContent = fs.readFileSync(csvPath, 'utf-8')
  const rows = parseCsv(csvContent)

  console.log(`Uploading ${rows.length} items from ${csvPath}`)

  const items = rows.map(row => ({
    id: row.validation_id,
    validation_id: row.validation_id,
    language: row.language,
    proverb: row.proverb,
    option_a: row.option_A,
    option_b: row.option_B,
    option_c: row.option_C,
    option_d: row.option_D,
    correct_label: row.correct_label,
    gold_meaning: row.correct_meaning,
    is_attention_check: false,
    item_metadata: {
      generator_model: row.generator_model,
      variant: row.variant,
      mcq_id: row.mcq_id,
      generation_status: row.generation_status,
      fallback_count: parseInt(row.fallback_count) || 0,
      consensus_label: row.consensus_label,
      consensus_frac: parseFloat(row.consensus_frac) || 0,
    },
  }))

  const attentionChecks = [
    {
      id: 'ATTN_001',
      validation_id: 'ATTN_001',
      language: 'English',
      proverb: 'ATTENTION CHECK: Please select option B for this item.',
      option_a: 'Wrong answer A',
      option_b: 'Correct answer - select B',
      option_c: 'Wrong answer C',
      option_d: 'Wrong answer D',
      correct_label: 'B',
      gold_meaning: 'Attention check - select B',
      is_attention_check: true,
      item_metadata: { is_attention_check: true },
    },
    {
      id: 'ATTN_002',
      validation_id: 'ATTN_002',
      language: 'English',
      proverb: 'ATTENTION CHECK: Please select option C for this item.',
      option_a: 'Wrong answer A',
      option_b: 'Wrong answer B',
      option_c: 'Correct answer - select C',
      option_d: 'Wrong answer D',
      correct_label: 'C',
      gold_meaning: 'Attention check - select C',
      is_attention_check: true,
      item_metadata: { is_attention_check: true },
    },
  ]

  const allItems = [...items, ...attentionChecks]
  const batchSize = 50
  let uploaded = 0
  let failed = 0

  for (let i = 0; i < allItems.length; i += batchSize) {
    const batch = allItems.slice(i, i + batchSize)
    try {
      await request('/rest/v1/pg_annotation_items?on_conflict=id', 'POST', batch)
      uploaded += batch.length
      console.log(`Uploaded batch ${Math.floor(i / batchSize) + 1}: ${uploaded}/${allItems.length}`)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      console.error(`Batch ${Math.floor(i / batchSize) + 1} failed:`, message)
      failed += batch.length
    }
  }

  console.log(`\nUpload complete: ${uploaded} items uploaded, ${failed} failed`)

  // Verify count
  const countResult = await request('/rest/v1/pg_annotation_items?select=count', 'GET')
  console.log(`Total items in DB: ${JSON.stringify(countResult).substring(0, 100)}`)
}

uploadItems().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})
