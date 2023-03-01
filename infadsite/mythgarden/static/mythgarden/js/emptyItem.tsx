'use strict'

import React from 'react'

const EMPTY_ITEM_SLOT_CONSTANT = 9000000

export default function EmptyItem ({ slotNumber }: EmptyItemProps): JSX.Element {
  return (
    <li className="item empty-slot" key={slotNumber + EMPTY_ITEM_SLOT_CONSTANT}>
      <span className="type">⬜️</span><span className="name">Empty</span>
    </li>
  )
}

interface EmptyItemProps {
  slotNumber: number
}
