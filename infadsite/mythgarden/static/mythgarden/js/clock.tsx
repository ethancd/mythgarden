'use strict'

import React from 'react'

export default function Clock ({ display }: Pick<ClockProps, 'display'>): JSX.Element {
  return (
        <div id="clock">{display}</div>
  )
}

interface ClockProps {
  display: string
  time: number
  dayNumber: number
}

export { Clock, type ClockProps }
