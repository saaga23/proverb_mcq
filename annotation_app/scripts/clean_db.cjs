const https = require('https')
require('dotenv').config({ path: '.env.local' })
const url = process.env.NEXT_PUBLIC_SUPABASE_URL
const key = process.env.SUPABASE_SERVICE_ROLE_KEY
function patch(p, body) {
  return new Promise((res, rej) => {
    const r = https.request({ hostname: new URL(url).hostname, path: p, method: 'PATCH', headers: { 'apikey': key, 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'Prefer': 'return=representation' } }, x => { let d = ''; x.on('data', c => d += c); x.on('end', () => res({ status: x.statusCode, body: d.slice(0, 200) })) })
    r.on('error', rej); r.write(JSON.stringify(body)); r.end()
  })
}
function del(p) {
  return new Promise((res, rej) => {
    const r = https.request({ hostname: new URL(url).hostname, path: p, method: 'DELETE', headers: { 'apikey': key, 'Authorization': 'Bearer ' + key } }, x => { let d = ''; x.on('data', c => d += c); x.on('end', () => res({ status: x.statusCode, body: d.slice(0, 200) })) })
    r.on('error', rej); r.end()
  })
}
;(async () => {
  try {
    const u = await patch('/rest/v1/pg_annotation_items?lock_expires_at=not.is.null', { lock_expires_at: null })
    console.log('unlock stale locks:', u.status, u.body)
    const d = await del('/rest/v1/pg_annotations?id=not.is.null')
    console.log('clear test annotations:', d.status, d.body)
    const c = await new Promise((res, rej) => { const r = https.request({ hostname: new URL(url).hostname, path: '/rest/v1/pg_annotation_items?select=count', method: 'GET', headers: { 'apikey': key, 'Authorization': 'Bearer ' + key } }, x => { let d = ''; x.on('data', c => d += c); x.on('end', () => res({ status: x.statusCode, body: d })) }); r.on('error', rej); r.end() })
    console.log('items remaining:', c.status, c.body)
  } catch (e) { console.error('ERR', e.message) }
})()
