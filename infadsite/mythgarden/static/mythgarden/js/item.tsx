'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Item ({ name, emoji, id, rarity, has_been_watered }: ItemProps): JSX.Element {
  return (
        <li
            className={`item ${rarity} ${has_been_watered ? 'watered' : ''}`}
            key={id}
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className='item-name'>{name}</span>
        </li>
  )
}

interface ItemProps {
  name: string
  emoji: string
  id: number
  rarity: string
  has_been_watered: boolean
}

export { Item, type ItemProps }
