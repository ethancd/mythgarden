'use strict'

import React, {useContext} from 'react'
import {Affinity, AffinityProps} from "./affinity";
import ActionPill, {ActionPillProps} from "./action";
import { useDrop } from "react-dnd";
import {DraggableGiftProps} from "./draggableGift";
import {postAction} from "./ajax";
import {ImageFilterContext} from "./lightColorLogic";

const GIFT_DIGEST_TEMPLATE = `GIVE-giftId-villagerId`

export default function Villager ({ name, imageUrl, affinity, description, id, actionPill, isGiftReceiver}: VillagerProps): JSX.Element {
  const { backgroundColor, opacity } = useContext(ImageFilterContext)
  const [{isOver, canDrop}, dropRef] = useDrop(() => ({
    accept: 'GIFT',
    drop: (item: DraggableGiftProps, monitor) => {
      const digest = GIFT_DIGEST_TEMPLATE.replace('giftId', `${item.giftData.id}`).replace('villagerId',  `${id}`)
      void postAction(digest)
    },
    canDrop: () => isGiftReceiver,
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop()
    })
  }))

  const highlight = canDrop && isGiftReceiver
  const ignore = isOver && !highlight

  return (
    <li
      className={`villager${highlight ? ' highlighted' : ''}${ignore ? ' no-hover-filter': ''}`}
      key={id}
      data-entity-id={id}
      ref={dropRef}>
      <div className="row">
        <div className="portrait">
          <img src={imageUrl}></img>
          { actionPill != null
            ? <ActionPill {...actionPill}></ActionPill>
            : null
          }
          <div className='portrait-filter' style={{ backgroundColor, opacity }}></div>
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
  actionPill: ActionPillProps
  isGiftReceiver: boolean
}

export { Villager, type VillagerProps, type VillagerData }
