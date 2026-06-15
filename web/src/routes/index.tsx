import { createFileRoute } from '@tanstack/react-router'

import { BridgeApp } from '../components/BridgeApp'

export const Route = createFileRoute('/')({
  component: BridgeApp,
})
