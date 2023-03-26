'use strict'

import React from 'react'

export default function Item ({ name, emoji, id, rarity, hasBeenWatered, quantity }: ItemProps): JSX.Element {
  return (
        <li
            className={`item ${rarity}${hasBeenWatered ? ' watered' : ''}`}
            key={id}
        >
            <span className='type'>{emoji}</span>
            {quantity != null ? <span className='quantity'>x{quantity}</span> : null}
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
  quantity?: number
}

export { Item, type ItemProps }
