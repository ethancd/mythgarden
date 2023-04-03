'use strict'

import React from 'react'
import { postAction } from './ajax'
import {Affinity, AffinityProps} from "./affinity";

const GIFT_DIGEST_TEMPLATE = `GIVE-giftId-villagerId`

export default function Villager ({ name, imageUrl, affinity, description, id, activeGiftId }: VillagerProps): JSX.Element {
  function giveGift(): void {
    if (activeGiftId == null) return

    const digest = GIFT_DIGEST_TEMPLATE.replace('giftId', `${activeGiftId}`).replace('villagerId',  `${id}`)
    void postAction(digest)
  }

  return (
    <li
      className={`villager${activeGiftId != null ? ' highlighted' : ''}`}
      key={id}
      data-entity-id={id}
      onClick={giveGift}>
      <div className="row">
        <div className="portrait">
          <img src={imageUrl}></img>
        </div>
        <div className="column">
          <Affinity {...affinity}></Affinity>
        </div>
      </div>
      <span className="name">{name}</span>
      <span className="description">{description}</span>
    </li>
  )
}

type VillagerProps = VillagerData & VillagerExtras

interface VillagerData {
  name: string
  imageUrl: string
  description: string
  id: number
  affinity: AffinityProps
}

interface VillagerExtras {
  activeGiftId: number | null
}

export { Villager, type VillagerProps, type VillagerData }
