'use strict'

import React from 'react'

export default function Message ({ text, id }: MessageProps): JSX.Element {
  return (
    <div className="message" key={id}>{text}</div>
  )
}

interface MessageProps {
  text: string
  id: number
}

export { Message, type MessageProps }
