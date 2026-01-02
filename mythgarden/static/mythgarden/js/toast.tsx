'use strict'

import React from 'react'
import { type ToastMessage } from './toastContainer'

export default function Toast({ text, isError, createdAt, state }: ToastMessage): JSX.Element {
  const age = Date.now() - createdAt

  // Calculate opacity during fade phase (3s-6s)
  let opacity = 1
  if (state === 'fading') {
    const fadeProgress = (age - 3000) / 3000 // 0 to 1
    opacity = 1 - fadeProgress
  }

  return (
    <div
      className={`toast ${isError ? 'error' : ''}`}
      style={{ opacity }}
    >
      {text}
    </div>
  )
}
