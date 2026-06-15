import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { BridgeApp } from './BridgeApp'

describe('BridgeApp', () => {
  it('renders the table as the first screen', () => {
    render(<BridgeApp />)

    expect(screen.getByRole('main').className).toContain('bridge-app')
    expect(screen.getByRole('group', { name: /human seats/i })).not.toBeNull()
    expect(screen.getByRole('region', { name: /current deal/i })).not.toBeNull()
  })

  it('supports 0 human watch mode from the setup controls', () => {
    render(<BridgeApp />)

    fireEvent.click(screen.getByRole('button', { name: /south/i }))

    expect(screen.getByText('Watch mode')).not.toBeNull()
  })

  it('toggles practice mode to show all hands', () => {
    render(<BridgeApp />)

    fireEvent.click(screen.getByRole('button', { name: /practice/i }))

    expect(screen.getByRole('button', { name: /practice/i }).className).toContain('active')
    expect(screen.getAllByLabelText(/hand/i).length).toBe(4)
  })
})
