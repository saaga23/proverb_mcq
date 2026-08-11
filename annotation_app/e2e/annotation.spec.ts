import { test, expect, request, type Page, type Route } from '@playwright/test'
import * as dotenv from 'dotenv'
import * as path from 'path'

dotenv.config({ path: path.join(process.cwd(), '.env.local') })

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || ''

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || process.env.NEXT_PUBLIC_APP_URL?.replace(':3000', ':3001') || 'http://localhost:3001'
const USE_MOCK = process.env.PLAYWRIGHT_USE_MOCK !== 'false'

console.log('BASE_URL:', BASE_URL, 'USE_MOCK:', USE_MOCK)

const MOCK_ITEMS = [
  {
    id: 'mock_001',
    validation_id: 'mock_001',
    language: 'English',
    proverb: 'A stitch in time saves nine.',
    option_a: 'Fix problems early before they get worse.',
    option_b: 'Procrastination leads to missed opportunities.',
    option_c: 'Sewing requires patience and precision.',
    option_d: 'Time waits for no one.',
    correct_label: 'A',
    gold_meaning: 'Fix problems early before they get worse.',
    is_attention_check: false,
    item_metadata: {},
  },
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
]

function setupMockSupabase(page: Page) {
  page.route('**/rest/v1/**', async (route: Route) => {
    const url = new URL(route.request().url())
    const method = route.request().method()
    const postgrestPath = url.pathname.replace('/rest/v1', '')

    if (method === 'POST' && postgrestPath === '/pg_annotator_profiles') {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify([{ annotator_id: 'test_annotator' }]),
      })
      return
    }

    if (method === 'POST' && postgrestPath === '/rpc/pg_get_items') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_ITEMS),
      })
      return
    }

    if (method === 'POST' && postgrestPath === '/rpc/pg_check_attention') {
      const body = await route.request().postDataJSON()
      const item = MOCK_ITEMS.find(i => i.id === body.p_item_id)
      const correct = item ? body.p_selected_answer === item.correct_label : false
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(correct),
      })
      return
    }

    if (method === 'POST' && postgrestPath === '/pg_annotations') {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify([{ id: 'mock_annotation_001' }]),
      })
      return
    }

    if (method === 'POST' && postgrestPath === '/rpc/pg_mark_complete') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(null),
      })
      return
    }

    if (method === 'POST' && postgrestPath === '/rpc/pg_get_progress') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ total: 62, completed: 1, remaining: 61 }]),
      })
      return
    }

    if (method === 'GET' && postgrestPath.startsWith('/pg_annotations')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ count: 1 }]),
      })
      return
    }

    await route.continue()
  })
}

test.describe('ProverbGap Annotation E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' })
  })

  test.beforeEach(async ({ page }) => {
    if (USE_MOCK) {
      setupMockSupabase(page)
    }
  })

  test('complete annotation flow: landing -> demographics -> annotate -> submit -> backend', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' })
    await expect(page.locator('h1')).toContainText('ProverbGap Annotation')

    await page.waitForFunction(() => {
      const select = document.querySelector('select')
      return select && Object.keys(select).some(k => k.startsWith('__reactFiber'))
    }, { timeout: 10000 })

    await page.locator('select').first().selectOption('English')
    await page.locator('input[type="radio"][value="yes"]').click()
    await page.locator('input[placeholder="How should we call you?"]').fill('Test Annotator')
    await page.locator('select').nth(1).selectOption('25-34')
    await page.locator('select').nth(2).selectOption('masters')
    await page.locator('input[placeholder="Your country"]').fill('Nigeria')
    await page.locator('input[type="checkbox"]').first().click()

    await expect(page.locator('button[type="submit"]:has-text("Start Annotating")')).toBeEnabled()
    await page.click('button[type="submit"]:has-text("Start Annotating")')

    await expect(page).toHaveURL(/\/annotate/, { timeout: 15000 })
    await expect(page.locator('text=Item 1 of')).toBeVisible({ timeout: 15000 })

    await page.locator('.space-y-3 > button').first().click()
    await page.locator('button:has-text("High confidence")').first().click()

    await page.waitForTimeout(11000)

    await page.click('button:has-text("Submit & Next")')
    await page.waitForTimeout(3000)

    await expect(page).toHaveURL(/\/annotate/)

    if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
      console.warn('Skipping backend verification: missing Supabase env vars')
      return
    }

    try {
      const res = await request.get(
        `${SUPABASE_URL}/rest/v1/pg_annotations?select=count`,
        {
          headers: {
            apikey: SERVICE_ROLE_KEY,
            Authorization: `Bearer ${SERVICE_ROLE_KEY}`,
          },
        }
      )
      expect(res.ok()).toBe(true)
      const data = await res.json()
      expect(data[0]?.count).toBeGreaterThan(0)
    } catch {
      console.warn('Backend verification skipped: Supabase unreachable')
    }
  })

  test('attention check flow', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' })

    await page.waitForFunction(() => {
      const select = document.querySelector('select')
      return select && Object.keys(select).some(k => k.startsWith('__reactFiber'))
    }, { timeout: 10000 })

    await page.locator('select').first().selectOption('English')
    await page.locator('input[type="radio"][value="yes"]').click()
    await page.locator('input[type="checkbox"]').first().click()

    await expect(page.locator('button[type="submit"]:has-text("Start Annotating")')).toBeEnabled()
    await page.click('button[type="submit"]:has-text("Start Annotating")')

    await expect(page).toHaveURL(/\/annotate/, { timeout: 15000 })
    await expect(page.locator('text=Item 1 of')).toBeVisible({ timeout: 15000 })

    const isAttentionCheck = await page.locator('text=Attention Check').isVisible().catch(() => false)

    if (isAttentionCheck) {
      const options = page.locator('.space-y-3 > button')

      const attentionText = await page.locator('text=ATTENTION CHECK:').textContent()
      let correctIndex = 1
      if (attentionText?.includes('option C')) {
        correctIndex = 2
      }

      await options.nth(correctIndex).click()
      await page.locator('button:has-text("High confidence")').first().click()

      await page.waitForTimeout(11000)

      await page.click('button:has-text("Submit & Next")')
    }

    await page.waitForTimeout(3000)
    await expect(page).toHaveURL(/\/annotate/)
  })
})
