'use strict'

import React from 'react'

export default function Item ({ name, emoji, id, rarity, hasBeenWatered }: ItemProps): JSX.Element {
  return (
        <li
            className={`item ${rarity}${hasBeenWatered ? ' watered' : ''}`}
            key={id}
        >
            <span className='type'>{emoji}</span>
            <span className='name'>{name}</span>
        </li>
  )
}

interface ItemProps {
  name: string
  emoji: string
  id: number
  rarity: string
  hasBeenWatered: boolean
}

export { Item, type ItemProps }
