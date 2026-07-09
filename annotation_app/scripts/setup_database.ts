import { createClient } from '@supabase/supabase-js'
import * as fs from 'fs'
import * as path from 'path'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials')
  process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function setupDatabase() {
  console.log('Setting up database...')

  // Read schema
  const schemaPath = path.join(__dirname, '..', 'supabase', 'schema.sql')
  const schemaContent = fs.readFileSync(schemaPath, 'utf-8')

  // Read RPCs
  const rpcPath = path.join(__dirname, '..', 'supabase', 'rpc.sql')
  const rpcContent = fs.readFileSync(rpcPath, 'utf-8')

  // Execute schema using exec_sql RPC (need to create this first in Supabase SQL Editor)
  console.log('Note: Please run supabase/schema.sql and supabase/rpc.sql in Supabase SQL Editor first')
  console.log('Then run: npm run upload-items')
}

setupDatabase().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})
