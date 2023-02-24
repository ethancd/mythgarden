'use strict'

import React from 'react'

export default function Clock ({ value }: ClockProps): JSX.Element {
  return (
        <li className="clock">{value}</li>
  )
}

interface ClockProps {
  value: string
}

export { Clock, type ClockProps }
