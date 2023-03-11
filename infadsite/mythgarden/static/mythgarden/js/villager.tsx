'use strict'

import React from 'react'
import { postAction } from './ajax'

const GIFT_DIGEST_TEMPLATE = `GIVE-giftId-villagerId`

export default function Villager ({ name, imageUrl, affinity, description, id, activeGiftId }: VillagerProps): JSX.Element {
  function giveGift(): void {
    console.log(activeGiftId)
    if (activeGiftId == null) return

    const digest = GIFT_DIGEST_TEMPLATE.replace('giftId', `${activeGiftId}`).replace('villagerId',  `${id}`)
    console.log(digest)
    void postAction(digest)
  }

  return (
    <li className={`villager${activeGiftId != null ? ' highlighted' : ''}`} key={id} onClick={giveGift}>
      <div className="row">
        <div className="portrait">
          <img src={imageUrl}></img>
        </div>
        <div className="column">
          <span className="name">{name}</span>
          <span className="affinity">{affinity}</span>
        </div>
      </div>
      <span className="description">{description}</span>
    </li>
  )
}

type VillagerProps = VillagerData & VillagerExtras

interface VillagerData {
  name: string
  imageUrl: string
  affinity: string
  description: string
  id: number
}

interface VillagerExtras {
  activeGiftId: number | null
}

export { Villager, type VillagerProps, type VillagerData }
