import { expect, test, type Locator, type Page } from '@playwright/test'

test('plays through a bridge deal without browser errors', async ({ page }) => {
  const errors = collectBrowserErrors(page)

  await page.goto('/')
  await expect(page.getByRole('main')).toHaveClass(/bridge-app/)
  await expect(page.getByRole('region', { name: 'Bridge table' })).toBeVisible()

  await playCurrentDeal(page)

  await expect(page.locator('.rail-status')).toContainText(/Board complete|Board passed out/)
  expect(errors()).toEqual([])
})

test('keeps move history scrollable instead of expanding the table', async ({ page }) => {
  await page.setViewportSize({ width: 1000, height: 700 })

  await page.goto('/')
  await buildMoveHistory(page, 18)

  const history = page.getByRole('region', { name: 'Move history' })
  const historyList = history.locator('ol')

  await expect(history).toBeVisible()
  await expect.poll(async () => historyList.evaluate((list) => ({
    clientHeight: list.clientHeight,
    overflowY: window.getComputedStyle(list).overflowY,
    scrollHeight: list.scrollHeight,
    scrollTop: list.scrollTop,
  }))).toMatchObject({
    overflowY: 'auto',
  })

  const historyMetrics = await historyList.evaluate((list) => ({
    clientHeight: list.clientHeight,
    scrollHeight: list.scrollHeight,
    scrollTop: list.scrollTop,
  }))
  expect(historyMetrics.scrollHeight).toBeGreaterThan(historyMetrics.clientHeight)
  expect(historyMetrics.scrollTop).toBeGreaterThan(0)

  const layoutMetrics = await history.evaluate((element) => ({
    historyHeight: element.getBoundingClientRect().height,
    maxHeight: Number.parseFloat(window.getComputedStyle(element).maxHeight),
  }))
  expect(layoutMetrics.historyHeight).toBeLessThanOrEqual(layoutMetrics.maxHeight + 1)
})

test('keeps the table usable on mobile screens', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })

  await page.goto('/')
  await expect(page.getByRole('region', { name: 'Bidding box' })).toBeVisible()
  await expect(page.getByRole('group', { name: 'Human seats' })).toBeVisible()
  await expect(page.locator('.mobile-history')).toBeVisible()

  const layout = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth
    const visibleButtons = Array.from(document.querySelectorAll('button'))
      .map((button) => button.getBoundingClientRect())
      .filter((box) => box.width > 0 && box.height > 0)

    return {
      horizontalOverflow: document.documentElement.scrollWidth - viewportWidth,
      offscreenButtons: visibleButtons.filter((box) => box.left < -1 || box.right > viewportWidth + 1).length,
    }
  })

  expect(layout.horizontalOverflow).toBeLessThanOrEqual(1)
  expect(layout.offscreenButtons).toBe(0)
})

async function playCurrentDeal(page: Page) {
  for (let actionCount = 0; actionCount < 160; actionCount += 1) {
    const dealText = await page.locator('.rail-status').innerText()
    if (/Board complete|Board passed out|Complete|Passed out/.test(dealText)) return

    if (await clickIfEnabled(page.getByRole('button', { name: 'Pass' }))) continue

    const playableCard = page.locator('button[aria-label^="Play "]:not([disabled])').first()
    if (await playableCard.isVisible().catch(() => false)) {
      await playableCard.click()
      continue
    }

    if (await clickIfEnabled(page.getByRole('button', { name: 'Step' }))) continue

    await page.waitForTimeout(80)
  }

  throw new Error('The deal did not settle within the browser smoke-test action limit.')
}

async function buildMoveHistory(page: Page, minimumItems: number) {
  const historyItems = page.getByRole('region', { name: 'Move history' }).locator('li')

  for (let actionCount = 0; actionCount < 80; actionCount += 1) {
    if (await historyItems.count() >= minimumItems) return

    if (await clickIfEnabled(page.getByRole('button', { name: 'Pass' }))) continue

    const playableCard = page.locator('button[aria-label^="Play "]:not([disabled])').first()
    if (await playableCard.isVisible().catch(() => false)) {
      await playableCard.click()
      continue
    }

    if (await clickIfEnabled(page.getByRole('button', { name: 'Step' }))) continue

    await page.waitForTimeout(80)
  }

  throw new Error(`Move history did not reach ${minimumItems} items.`)
}

async function clickIfEnabled(locator: Locator) {
  if (!(await locator.isVisible().catch(() => false))) return false
  if (!(await locator.isEnabled().catch(() => false))) return false
  await locator.click()
  return true
}

function collectBrowserErrors(page: Page) {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text())
  })
  return () => errors
}
