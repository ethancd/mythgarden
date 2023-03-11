'use strict'

import React from 'react'

const LATE_WARNING_TIME = 20 * 60
const VERY_LATE_WARNING_TIME = 22 * 60
const VERY_VERY_LATE_WARNING_TIME = 23.5 * 60

export default function Clock ({ display, time }: Pick<ClockProps, 'display' | 'time'>): JSX.Element {
  function getLateness(time: number) {
    if (time >= VERY_VERY_LATE_WARNING_TIME) return 'very-very-late'
    if (time >= VERY_LATE_WARNING_TIME) return 'very-late'
    if (time >= LATE_WARNING_TIME) return 'late'
    return ''
  }

  const lateness = getLateness(time)

  return (
        <div id="clock" className={lateness}>{display}</div>
  )
}

interface ClockProps {
  display: string
  time: number
  dayNumber: number
}

export { Clock, type ClockProps }
