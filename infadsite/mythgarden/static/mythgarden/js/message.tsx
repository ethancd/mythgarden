'use strict'

import React from 'react'

export default function Message ({ value, id }: MessageProps): JSX.Element {
  return (
    <div className="message" key={id}>{value}</div>
  )
}

interface MessageProps {
  value: string
  id: number
}

export { Message, type MessageProps }
