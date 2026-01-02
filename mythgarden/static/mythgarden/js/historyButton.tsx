'use strict'

import React from 'react'

export default function HistoryButton({ onClick }: { onClick: () => void }): JSX.Element {
  return (
    <button className="history-button" onClick={onClick} title="Message History">
      📜
    </button>
  )
}
