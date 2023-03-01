'use strict'

import React from 'react'

export default function Message ({ value }: MessageProps): JSX.Element {
  return (
    <div className="message">{value}</div>
  )
}

interface MessageProps {
  value: string
}

export { Message, type MessageProps }
