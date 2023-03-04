'use strict'

import React from 'react'

export default function Clock ({ value }: ClockProps): JSX.Element {
  return (
        <div id="clock">{value}</div>
  )
}

interface ClockProps {
  value: string
}

export { Clock, type ClockProps }
