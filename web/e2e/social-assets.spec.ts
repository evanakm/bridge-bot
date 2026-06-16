import { expect, test, type APIRequestContext, type Page } from '@playwright/test'

test('publishes Twitter, Open Graph, and install metadata', async ({ page, request }) => {
  await page.goto('/')

  await expect(page).toHaveTitle('Bridge Bot Table')
  await expect(page.locator('meta[name="description"]')).toHaveAttribute('content', /Play a complete bridge hand/)
  await expect(page.locator('meta[property="og:type"]')).toHaveAttribute('content', 'website')
  await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', 'https://bridge.masonbrothers.ca/social-card.png')
  await expect(page.locator('meta[property="og:image:type"]')).toHaveAttribute('content', 'image/png')
  await expect(page.locator('meta[property="og:image:width"]')).toHaveAttribute('content', '1200')
  await expect(page.locator('meta[property="og:image:height"]')).toHaveAttribute('content', '630')
  await expect(page.locator('meta[name="twitter:card"]')).toHaveAttribute('content', 'summary_large_image')
  await expect(page.locator('meta[name="twitter:image"]')).toHaveAttribute('content', 'https://bridge.masonbrothers.ca/social-card.png')
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', 'https://bridge.masonbrothers.ca/')
  await expect(page.locator('link[rel="manifest"]')).toHaveAttribute('href', '/site.webmanifest')
  await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute('href', '/apple-touch-icon.png')
  await expect(page.locator('link[rel="icon"][type="image/png"]')).toHaveAttribute('href', '/favicon-32.png')

  await expectImageSize(page, '/social-card.png', { width: 1200, height: 630 })
  await expectImageSize(page, '/apple-touch-icon.png', { width: 180, height: 180 })
  await expectImageSize(page, '/app-icon-192.png', { width: 192, height: 192 })
  await expectImageSize(page, '/app-icon-512.png', { width: 512, height: 512 })
  await expectOkAsset(request, '/favicon.svg', 'image/svg+xml')
  await expectOkAsset(request, '/favicon-32.png', 'image/png')

  const manifestResponse = await request.get('/site.webmanifest')
  expect(manifestResponse.ok()).toBe(true)
  expect(manifestResponse.headers()['content-type']).toContain('application/manifest+json')

  const manifest = await manifestResponse.json()
  expect(manifest).toMatchObject({
    name: 'Bridge Bot Table',
    short_name: 'Bridge Bot',
    display: 'standalone',
    background_color: '#10241d',
    theme_color: '#123827',
  })
  expect(manifest.icons).toEqual([
    {
      src: '/app-icon-192.png',
      sizes: '192x192',
      type: 'image/png',
      purpose: 'any',
    },
    {
      src: '/app-icon-512.png',
      sizes: '512x512',
      type: 'image/png',
      purpose: 'any maskable',
    },
  ])
})

async function expectOkAsset(request: APIRequestContext, path: string, contentType: string) {
  const response = await request.get(path)
  expect(response.ok()).toBe(true)
  expect(response.headers()['content-type']).toContain(contentType)
}

async function expectImageSize(page: Page, path: string, expected: { width: number; height: number }) {
  const size = await page.evaluate(async (src) => {
    const image = new Image()
    image.src = src
    await image.decode()
    return {
      height: image.naturalHeight,
      width: image.naturalWidth,
    }
  }, path)

  expect(size).toEqual(expected)
}
