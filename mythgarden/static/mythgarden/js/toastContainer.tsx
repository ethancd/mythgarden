'use strict'

import React, { useState, useEffect, useRef } from 'react'
import Toast from './toast'
import { type MessageProps } from './message'

interface ToastMessage {
  id: number
  text: string
  isError: boolean
  createdAt: number
  state: 'visible' | 'fading' | 'removed'
}

export default function ToastContainer({ messages }: { messages: MessageProps[] }): JSX.Element {
  const [toasts, setToasts] = useState<ToastMessage[]>([])
  const seenMessageIds = useRef<Set<number>>(new Set())

  // Track new messages and create toasts
  useEffect(() => {
    messages.forEach(msg => {
      if (!seenMessageIds.current.has(msg.id)) {
        seenMessageIds.current.add(msg.id)
        setToasts(prev => [...prev, {
          ...msg,
          createdAt: Date.now(),
          state: 'visible'
        }])
      }
    })
  }, [messages])

  // Timer to transition toast states
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now()
      setToasts(prev => prev
        .map(toast => {
          const age = now - toast.createdAt
          if (age > 6000) {
            return { ...toast, state: 'removed' as const }
          } else if (age > 3000) {
            return { ...toast, state: 'fading' as const }
          }
          return toast
        })
        .filter(toast => toast.state !== 'removed')
      )
    }, 100)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <Toast key={toast.id} {...toast} />
      ))}
    </div>
  )
}

export { type ToastMessage }
