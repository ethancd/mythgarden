'use strict'

import React from 'react'

export default function EmptyItem ({ slotNumber }: EmptyItemProps): JSX.Element {
  return (
    <li className="item empty-slot" key={`empty-slot-${slotNumber}`}>
      <span className="type">⬜️</span><span className="name">Empty</span>
    </li>
  )
}

interface EmptyItemProps {
  slotNumber: number
}
