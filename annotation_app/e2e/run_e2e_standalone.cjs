const { chromium } = require('@playwright/test')
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env.local') })

const BASE = process.env.E2E_BASE_URL || 'http://localhost:3000'
const SUPABASE_URL = 'https://bzqpzhkhnytrinzyqraz.supabase.co'
// Read the service-role key from the environment; never hardcode secrets in source.
// e.g. set SUPABASE_SERVICE_ROLE_KEY in annotation_app/.env.local (gitignored) before running.
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY
if (!SERVICE_ROLE_KEY) {
  console.error('SUPABASE_SERVICE_ROLE_KEY not set. Export it (e.g. from .env.local) before running the e2e check.')
  process.exit(1)
}

function annCount() {
  return new Promise((res, rej) => {
    const https = require('https')
    const r = https.request({ hostname: new URL(SUPABASE_URL).hostname, path: '/rest/v1/pg_annotations?select=count', method: 'GET', headers: { 'apikey': SERVICE_ROLE_KEY, 'Authorization': 'Bearer ' + SERVICE_ROLE_KEY } }, x => { let d = ''; x.on('data', c => d += c); x.on('end', () => res(JSON.parse(d)[0]?.count || 0)) })
    r.on('error', rej); r.end()
  })
}

;(async () => {
  console.log('launching browser...')
  const browser = await chromium.launch()
  const page = await browser.newPage()
  const pageErrors = []
  page.on('pageerror', e => pageErrors.push(e.message))
  page.on('console', m => { if (m.type() === 'error') pageErrors.push('console:' + m.text()) })

  const netLog = []
  page.on('request', r => { if (r.url().includes('/rest/v1/') ) netLog.push('REQ ' + r.method() + ' ' + r.url().replace(/https:\/\/[^/]+/, '') + ' :: ' + (r.postData() || '').slice(0, 120)) })
  page.on('response', r => { if (r.url().includes('/rest/v1/')) netLog.push('RES ' + r.status() + ' ' + r.url().replace(/https:\/\/[^/]+/, '') + ' :: ' + (r.request().method()) + ' ' + (r.body() ? '(body)' : '')) })

  // Fresh annotator
  await page.goto(BASE)
  await page.evaluate(() => localStorage.clear())

  // Landing
  await page.goto(BASE)
  await page.locator('h1').waitFor()
  if (!/ProverbGap Annotation/.test(await page.locator('h1').textContent())) throw new Error('landing h1 missing')
  console.log('PASS: landing page loaded')

  // Demographics
  await page.selectOption('select:has-text("Select language...")', 'English')
  await page.check('input[type="radio"][value="yes"]')
  await page.click('button[type="submit"]:has-text("Start Annotating")')
  await page.waitForURL(/\/annotate/, { timeout: 10000 })
  console.log('PASS: redirected to /annotate')

  // First item visible
  await page.locator('text=Item 1 of').waitFor({ timeout: 15000 })
  console.log('PASS: first item rendered')

  const before = await annCount()

  // Annotate item 1
  await page.locator('.space-y-3 > button').first().click()
  await page.locator('button:has-text("Correct")').first().click()
  await page.locator('button:has-text("High confidence")').first().click()
  await page.waitForTimeout(3500) // minimum time guard
  const canSubmit = await page.locator('button:has-text("Submit & Next")').isEnabled().catch(() => false)
  console.log('submit button enabled before click:', canSubmit)
  await page.click('button:has-text("Submit & Next")')
  await page.waitForTimeout(6000)

  let after = await annCount()
  if (after <= before) {
    // Retry once — could be a timing race on the lock/insert
    console.log('first submit did not persist yet; retrying once...')
    console.log('NETLOG so far:', netLog.join('\n'))
    await page.locator('.space-y-3 > button').first().click().catch(() => {})
    await page.locator('button:has-text("Correct")').first().click().catch(() => {})
    await page.locator('button:has-text("High confidence")').first().click().catch(() => {})
    await page.waitForTimeout(3500)
    await page.click('button:has-text("Submit & Next")').catch(() => {})
    await page.waitForTimeout(6000)
    after = await annCount()
  }

  const uiError = await page.locator('.bg-red-50').textContent().catch(() => null)
  console.log('UI error banner:', uiError)
  const uiMsg = await page.locator('h2:has-text("Batch Complete")').count()
  console.log('batch complete heading present:', uiMsg)

  if (after <= before) {
    console.log('NETLOG:', netLog.join('\n'))
    console.log('pageErrors:', pageErrors.join('\n'))
    throw new Error(`backend annotation not written (before=${before}, after=${after})`)
  }
  console.log(`PASS: annotation persisted to backend (before=${before}, after=${after})`)

  // Continue item 2 — inspect state if next item does not render
  try {
    await page.locator('text=Item 2 of').waitFor({ timeout: 15000 })
    console.log('PASS: advanced to next item (Item 2 of 10 rendered)')
  } catch (e2) {
    console.log('next-item NOT rendered. NETLOG:', netLog.join('\n'))
    console.log('pageErrors:', pageErrors.join('\n'))
    const heading = await page.locator('h2').allTextContents().catch(() => [])
    console.log('headings on page:', heading)
    await page.screenshot({ path: 'e2e/stuck_after_submit.png' }).catch(() => {})
    const bodyText = await page.locator('body').innerText().catch(() => '')
    console.log('BODY TEXT (first 700):', bodyText.slice(0, 700))
    throw e2
  }

  // Attention check probe (attempt to surface one within first few items)
  let sawAttention = false
  for (let i = 0; i < 6; i++) {
    if (await page.locator('text=Attention Check').isVisible().catch(() => false)) { sawAttention = true; break }
    await page.locator('.space-y-3 > button').first().click()
    await page.locator('button:has-text("Correct")').first().click()
    await page.locator('button:has-text("High confidence")').first().click()
    await page.waitForTimeout(3500)
    await page.click('button:has-text("Submit & Next")').catch(() => {})
    await page.waitForTimeout(2000)
    if (await page.locator('text=Batch Complete').isVisible().catch(() => false)) break
  }
  console.log(sawAttention ? 'PASS: attention-check banner renders when an attention item is served' : 'INFO: no attention item encountered in sampled batch (random order)')

  console.log('NETLOG:', netLog.join('\n'))
  console.log(pageErrors.length ? 'WARN: page errors:\n' + pageErrors.join('\n') : 'PASS: no page/console errors')

  await browser.close()
  console.log('\nE2E RESULT: PASS')
  process.exit(0)
})().catch(async (e) => {
  console.error('E2E RESULT: FAIL ->', e.message)
  process.exit(1)
})
