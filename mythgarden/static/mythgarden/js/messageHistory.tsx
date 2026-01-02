'use strict'

import React from 'react'
import { type MessageProps } from './message'

interface MessageHistoryProps {
  messages: MessageProps[]
  isOpen: boolean
  onClose: () => void
}

export default function MessageHistory({ messages, isOpen, onClose }: MessageHistoryProps): JSX.Element | null {
  if (!isOpen) return null

  // Reverse to show newest at top
  const reversedMessages = [...messages].reverse()

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="message-history-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Message History</h3>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>
        <div className="modal-content">
          {reversedMessages.map(msg => (
            <div
              key={msg.id}
              className={`history-message ${msg.isError ? 'error' : ''}`}
            >
              {msg.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export { type MessageHistoryProps }
