import * as fs from 'fs'
import * as path from 'path'
import * as dotenv from 'dotenv'

dotenv.config({ path: path.join(__dirname, '..', '.env.local') })

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!

function printDashboardInstructions(filename: string) {
  console.log('\n' + '='.repeat(70))
  console.log('DATABASE SETUP REQUIRED')
  console.log('='.repeat(70))
  console.log(`\nThe SQL file has been saved to: ${filename}`)
  console.log('\nPlease run it in the Supabase SQL Editor:')
  console.log(`  1. Open: ${supabaseUrl.replace('https://', 'https://dashboard.')}/project/${supabaseUrl.replace('https://', '')}/sql`)
  console.log('  2. Paste the contents of the SQL file')
  console.log('  3. Click "Run"')
  console.log('\n' + '='.repeat(70) + '\n')
}

async function setupDatabase() {
  console.log('Setting up ProverbGap annotation database...')

  const schemaPath = path.join(__dirname, '..', 'supabase', 'schema.sql')
  const schemaContent = fs.readFileSync(schemaPath, 'utf-8')

  const outputPath = path.join(__dirname, '..', 'supabase', 'run_in_dashboard.sql')
  fs.writeFileSync(outputPath, schemaContent)

  console.log(`SQL script saved to: ${outputPath}`)
  printDashboardInstructions(outputPath)

  console.log('After running the SQL in the dashboard:')
  console.log('  1. npm run upload-items   # Load your CSV data')
  console.log('  2. npm run dev            # Start the annotation app')
}

setupDatabase().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})
