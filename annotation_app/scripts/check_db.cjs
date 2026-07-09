const { Client } = require('pg')
const fs = require('fs')
const path = require('path')
require('dotenv').config({ path: path.join(__dirname, '..', '.env.local') })

const client = new Client({ connectionString: process.env.DATABASE_URL })
;(async () => {
  try {
    await client.connect()
    const tables = await client.query(`
      SELECT table_name FROM information_schema.tables
      WHERE table_schema='public' AND table_name LIKE 'pg_%'
      ORDER BY table_name`)
    console.log('pg_ tables:', tables.rows.map(r => r.table_name))
    const funcs = await client.query(`
      SELECT proname, pg_get_function_arguments(oid) AS args
      FROM pg_proc WHERE proname LIKE 'pg_%'
      ORDER BY proname`)
    console.log('pg_ functions:', funcs.rows.map(r => `${r.proname}(${r.args})`))
    const itemCount = await client.query('SELECT count(*)::int AS n FROM public.pg_annotation_items').catch(e => ({ rows: [{ n: 'ERR:' + e.message }] }))
    console.log('pg_annotation_items count:', itemCount.rows[0].n)
  } catch (e) {
    console.error('ERROR:', e.message)
  } finally {
    await client.end()
  }
})()
