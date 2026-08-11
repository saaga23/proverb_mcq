import { test, expect } from '@playwright/test'

test.describe('ProverbGap Annotation E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000')
    await page.evaluate(() => localStorage.clear())
  })

  test('complete annotation flow: landing -> demographics -> annotate -> submit -> backend', async ({ page }) => {
    await page.goto('http://localhost:3000')
    await expect(page.locator('h1')).toContainText('ProverbGap Annotation')

    await page.selectOption('select:has-text("Select language...")', 'English')
    await page.check('input[type="radio"][value="yes"]')
    await page.fill('input[placeholder="How should we call you?"]', 'Test Annotator')
    await page.selectOption('select:has-text("Select age group...")', '25-34')
    await page.selectOption('select:has-text("Select education level...")', 'masters')
    await page.fill('input[placeholder="Your country"]', 'Nigeria')

    await page.click('button[type="submit"]:has-text("Start Annotating")')

    await expect(page).toHaveURL(/\/annotate/, { timeout: 10000 })
    await expect(page.locator('text=Item 1 of')).toBeVisible({ timeout: 15000 })

    // Select first option
    await page.locator('.space-y-3 > button').first().click()

    // Select confidence using exact match
    await page.locator('button:has-text("High confidence")').first().click()

    // Wait for minimum time guard (10 seconds per AnnotationUI.tsx MIN_TIME_MS)
    await page.waitForTimeout(11000)

    // Click submit
    await page.click('button:has-text("Submit & Next")')

    // Wait for submission to complete
    await page.waitForTimeout(3000)

    // Verify we're still on annotate page
    await expect(page).toHaveURL(/\/annotate/)

    // Verify backend has annotations
    const annotationsExist = await page.evaluate(async () => {
      // These should be set in .env.test so they are not hardcoded in source control
      const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
      const SERVICE_ROLE_KEY = process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY || ''

      const response = await fetch(`${SUPABASE_URL}/rest/v1/pg_annotations?select=count`, {
        headers: {
          'apikey': SERVICE_ROLE_KEY,
          'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
        },
      })
      const data = await response.json()
      return data[0]?.count > 0
    })

    expect(annotationsExist).toBe(true)
  })

  test('attention check flow', async ({ page }) => {
    await page.goto('http://localhost:3000')

    await page.selectOption('select:has-text("Select language...")', 'English')
    await page.check('input[type="radio"][value="yes"]')
    await page.click('button[type="submit"]:has-text("Start Annotating")')

    await expect(page).toHaveURL(/\/annotate/, { timeout: 10000 })
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
