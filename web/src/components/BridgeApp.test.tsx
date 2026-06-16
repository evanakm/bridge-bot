import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { BridgeApp } from './BridgeApp'

describe('BridgeApp', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('renders the table as the first screen', () => {
    render(<BridgeApp />)

    expect(screen.getByRole('main').className).toContain('bridge-app')
    expect(screen.getByRole('group', { name: /human seats/i })).not.toBeNull()
    expect(screen.getByRole('region', { name: /current deal/i })).not.toBeNull()
    expect(screen.getByRole('region', { name: /bidding box/i }).parentElement?.className).toContain('felt-grid')
    expect(screen.getByText('North to bid')).not.toBeNull()
    expect(screen.getByText('Bot action')).not.toBeNull()
    expect(screen.getByText('Bidding')).not.toBeNull()
    expect(screen.getByText('Waiting')).not.toBeNull()
    expect(screen.getByRole('checkbox', { name: /share games/i })).not.toBeNull()
    expect(screen.getByRole('link', { name: /privacy/i }).getAttribute('href')).toBe('/privacy')
  })

  it('shows public move history instead of a bot pace control', () => {
    render(<BridgeApp />)

    expect(screen.queryByText(/bot pace/i)).toBeNull()

    const history = screen.getByRole('region', { name: /move history/i })
    expect(within(history).getByText(/waiting for the first call/i)).not.toBeNull()

    fireEvent.click(screen.getByRole('button', { name: /^Step$/i }))

    expect(within(history).queryByText(/waiting for the first call/i)).toBeNull()
    expect(within(history).getByText('Bid 1')).not.toBeNull()
    expect(within(history).getAllByText(/^North /i).length).toBeGreaterThan(0)
    expect(within(history).getAllByText('Bot call').length).toBeGreaterThan(0)
    expect(screen.getByLabelText(/latest move/i).textContent).toContain('North')
  })

  it('auto-advances bots only until the next human-controlled action', async () => {
    vi.useFakeTimers()
    render(<BridgeApp />)

    await act(async () => {
      await vi.advanceTimersByTimeAsync(420)
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(420)
    })

    expect(screen.getByText('South to bid')).not.toBeNull()
    expect(screen.getByText('Your call')).not.toBeNull()
    expect(screen.getByText('Waiting for South')).not.toBeNull()

    const history = screen.getByRole('region', { name: /move history/i })
    expect(within(history).getAllByText('North Pass').length).toBeGreaterThan(0)
    expect(within(history).getAllByText('East 1H').length).toBeGreaterThan(0)
    expect(within(history).queryByText(/^West /i)).toBeNull()

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000)
    })

    expect(screen.getByText('South to bid')).not.toBeNull()
    expect(within(history).queryByText(/^West /i)).toBeNull()
  })

  it('renders only legal bid controls for the human turn', async () => {
    vi.useFakeTimers()
    render(<BridgeApp />)

    await act(async () => {
      await vi.advanceTimersByTimeAsync(420)
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(420)
    })

    const biddingBox = screen.getByRole('region', { name: /bidding box/i })

    expect(screen.getByText('South to bid')).not.toBeNull()
    expect(within(biddingBox).queryByRole('button', { name: '1C' })).toBeNull()
    expect(within(biddingBox).queryByRole('button', { name: '1D' })).toBeNull()
    expect(within(biddingBox).queryByRole('button', { name: /redouble/i })).toBeNull()
    expect((within(biddingBox).getByRole('button', { name: /pass/i }) as HTMLButtonElement).disabled).toBe(false)
    expect(within(biddingBox).getAllByRole('button').every((button) => !button.hasAttribute('disabled'))).toBe(true)
  })

  it('supports 0 to 4 human seats from the setup controls', () => {
    render(<BridgeApp />)
    const seatControls = within(screen.getByRole('group', { name: /human seats/i }))

    fireEvent.click(seatControls.getByRole('button', { name: /north/i }))
    fireEvent.click(seatControls.getByRole('button', { name: /east/i }))
    fireEvent.click(seatControls.getByRole('button', { name: /west/i }))

    expect(screen.getByText('4-seat hotseat')).not.toBeNull()

    fireEvent.click(seatControls.getByRole('button', { name: /north/i }))
    fireEvent.click(seatControls.getByRole('button', { name: /east/i }))
    fireEvent.click(seatControls.getByRole('button', { name: /south/i }))
    fireEvent.click(seatControls.getByRole('button', { name: /west/i }))

    expect(screen.getByText('Watch mode')).not.toBeNull()
  })

  it('applies seat changes to the active game immediately', () => {
    render(<BridgeApp />)

    fireEvent.click(screen.getByRole('button', { name: /north/i }))

    expect(screen.getByRole('dialog', { name: /pass to north/i })).not.toBeNull()
  })

  it('shows the active seat badge on the current turn', () => {
    render(<BridgeApp />)

    expect(within(screen.getByRole('region', { name: /north seat/i })).getByText('to bid')).not.toBeNull()
  })

  it('advances dealer and vulnerability on new deals but not restarts', () => {
    render(<BridgeApp />)

    expect(screen.getByText('Board 1')).not.toBeNull()
    expect(screen.getByText('Dealer North')).not.toBeNull()
    expect(screen.getByText('Vul None')).not.toBeNull()

    fireEvent.click(screen.getByRole('button', { name: /^New$/i }))

    expect(screen.getByText('Board 2')).not.toBeNull()
    expect(screen.getByText('Dealer East')).not.toBeNull()
    expect(screen.getByText('Vul NS')).not.toBeNull()

    fireEvent.click(screen.getByRole('button', { name: /restart deal/i }))

    expect(screen.getByText('Board 2')).not.toBeNull()
    expect(screen.getByText('Dealer East')).not.toBeNull()
    expect(screen.getByText('Vul NS')).not.toBeNull()
  })

  it('toggles practice mode to show all hands', () => {
    const { container } = render(<BridgeApp />)

    fireEvent.click(screen.getByRole('button', { name: /practice/i }))

    expect(screen.getByRole('button', { name: /practice/i }).className).toContain('active')
    expect(screen.getAllByLabelText(/hand/i).length).toBe(4)
    expect(container.querySelectorAll('.playing-card')).toHaveLength(52)
    expect(screen.queryAllByRole('button', { name: /play /i })).toHaveLength(0)
  })

})
