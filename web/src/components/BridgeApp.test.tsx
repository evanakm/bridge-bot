import { fireEvent, render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { BridgeApp } from './BridgeApp'

describe('BridgeApp', () => {
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
    render(<BridgeApp />)

    fireEvent.click(screen.getByRole('button', { name: /practice/i }))

    expect(screen.getByRole('button', { name: /practice/i }).className).toContain('active')
    expect(screen.getAllByLabelText(/hand/i).length).toBe(4)
    expect(screen.getAllByRole('button', { name: /play /i })).toHaveLength(52)
  })
})
