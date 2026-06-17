import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/privacy')({
  component: PrivacyPage,
})

function PrivacyPage() {
  return (
    <main className="privacy-page">
      <article>
        <a href="/">Back to table</a>
        <span className="eyebrow">Bridge Bot</span>
        <h1>Privacy Policy</h1>
        <p>Effective June 16, 2026.</p>

        <h2>Game Recording</h2>
        <p>
          Game sharing is off by default. If you turn it on, Bridge Bot sends
          completed or passed-out boards to the backend so they can be used for
          bot training and evaluation.
        </p>

        <h2>What We Store</h2>
        <ul>
          <li>Board number, seed, dealer, vulnerability, and final phase.</li>
          <li>Seat controller types, auction, contract, tricks, score, and final hands.</li>
          <li>The privacy policy version attached to the consented record.</li>
        </ul>

        <h2>What We Do Not Store</h2>
        <ul>
          <li>Names, email addresses, account IDs, session IDs, or visitor IDs.</li>
          <li>IP addresses, user agents, browser details, or device details.</li>
          <li>Anything typed by a player, because the table has no chat or profile fields.</li>
        </ul>

        <h2>Training Use</h2>
        <p>
          Shared games may be used to compare bot policies, train future bridge
          models, test scoring and bidding behavior, and improve gameplay
          quality. Records are anonymous table data, not user profiles.
        </p>

        <h2>Control</h2>
        <p>
          Turn off Share games at any time to stop sending future boards. Boards
          already accepted by the backend may remain in the training dataset.
        </p>
      </article>
    </main>
  )
}
