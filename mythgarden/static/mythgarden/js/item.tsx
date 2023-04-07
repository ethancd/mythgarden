'use strict'

import React from 'react'
import ActionPill, {ActionPillProps} from "./action";

export default function Item ({ name, emoji, id, rarity, hasBeenWatered, quantity, actionPill }: ItemProps): JSX.Element {
  return (
        <li
            className={`item ${rarity}${hasBeenWatered ? ' watered' : ''}`}
            key={id}
            data-entity-id={id}
        >
            <span className='type'>{emoji}</span>
            {quantity != null ? <span className='quantity'>x{quantity}</span> : null}
            <span className='name'>{name}</span>
            { actionPill != null
              ? <ActionPill {...actionPill}></ActionPill>
              : null
            }
        </li>
  )
}

type ItemProps = ItemData & ItemExtras

interface ItemData {
  name: string
  emoji: string
  id: number
  rarity: string
  hasBeenWatered: boolean
  quantity?: number
}

interface ItemExtras {
  actionPill: ActionPillProps
}

export { Item, type ItemData }
