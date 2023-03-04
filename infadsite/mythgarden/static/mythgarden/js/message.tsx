'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Message ({ text, is_error, id }: MessageProps): JSX.Element {
  return (
    <div className={`message${is_error ? ' error' : ''}`} key={id}>{text}</div>
  )
}

interface MessageProps {
  text: string
  is_error: boolean
  id: number
}

export { Message, type MessageProps }
