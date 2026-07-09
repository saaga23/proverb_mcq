import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials')
  process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function checkExistingTables() {
  console.log('Checking existing tables in Supabase...\n')

  // Query information_schema to list all tables
  const { data, error } = await supabase
    .from('information_schema.tables')
    .select('table_name, table_schema')
    .eq('table_schema', 'public')
    .order('table_name')

  if (error) {
    console.error('Error querying tables:', error)
    // Try alternative method
    console.log('\nTrying alternative method...')
    const { data: tables, error: err2 } = await supabase
      .rpc('pg_catalog.pg_tables')
    
    if (err2) {
      console.error('Alternative method also failed:', err2)
      console.log('\nNote: Service role key may have expired.')
      console.log('Please get a new service role key from Supabase Dashboard > Settings > API')
      return
    }
  }

  console.log('Existing tables in public schema:')
  console.log('=' .repeat(50))
  
  if (data && data.length > 0) {
    data.forEach((table: any) => {
      console.log(`  - ${table.table_name}`)
    })
    console.log(`\nTotal: ${data.length} tables`)
  } else {
    console.log('  No tables found or unable to query')
  }

  // Check for potential conflicts
  console.log('\nChecking for potential conflicts with our schema:')
  console.log('=' .repeat(50))
  
  const ourTables = [
    'pg_annotation_items',
    'pg_annotator_profiles', 
    'pg_annotations'
  ]
  
  const existingTableNames = data?.map((t: any) => t.table_name) || []
  
  ourTables.forEach(table => {
    if (existingTableNames.includes(table)) {
      console.log(`  ⚠️  CONFLICT: ${table} already exists!`)
    } else {
      console.log(`  ✅ Safe to create: ${table}`)
    }
  })
}

checkExistingTables().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})
