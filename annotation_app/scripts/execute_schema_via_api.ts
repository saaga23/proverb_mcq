import * as fs from 'fs'
import * as path from 'path'
import * as dotenv from 'dotenv'
import https from 'https'

dotenv.config({ path: path.join(__dirname, '..', '.env.local') })

const MANAGEMENT_TOKEN = process.env.SUPABASE_MANAGEMENT_TOKEN!
const PROJECT_REF = 'bzqpzhkhnytrinzyqraz'
const SCHEMA_PATH = path.join(__dirname, '..', 'supabase', 'schema.sql')

if (!MANAGEMENT_TOKEN) {
  console.error('Missing SUPABASE_MANAGEMENT_TOKEN')
  process.exit(1)
}

const schemaContent = fs.readFileSync(SCHEMA_PATH, 'utf-8')

function request(path: string, method = 'GET', body: unknown = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.supabase.com',
      path,
      method,
      headers: {
        'Authorization': `Bearer ${MANAGEMENT_TOKEN}`,
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
          reject(new Error(`HTTP ${res.statusCode}: ${data.substring(0, 500)}`))
        }
      })
    })
    req.on('error', reject)
    if (body) req.write(JSON.stringify(body))
    req.end()
  })
}

async function executeSchema() {
  console.log('Executing full schema via Supabase Management API...')

  try {
    const result = await request(`/v1/projects/${PROJECT_REF}/database/query`, 'POST', {
      query: schemaContent
    })
    console.log('Schema executed successfully')
    console.log(JSON.stringify(result, null, 2).substring(0, 500))
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error'
    console.error('Schema execution failed:', message)
  }
}

executeSchema().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
