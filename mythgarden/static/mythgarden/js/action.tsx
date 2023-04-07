import React from 'react'
import Duration, { WaitClass } from "./duration";
import PriceTag from "./priceTag";

export default function ActionPill ({ emoji, costAmount, costType, waitClass }: ActionPillProps): JSX.Element {
  if (costAmount == null || costType == null) {
    return (
      <div className='action-pill'>
        <span className='action-type'>{emoji}</span>
      </div>
    )
  } else {
    return (
      <div className='action-pill'>
          { costType == CostType.Time
            ? <>
                <span className='action-type'>{emoji}</span>
                <Duration amount={costAmount} waitClass={waitClass}></Duration>
              </>
            : <PriceTag amount={costAmount}></PriceTag>
          }
      </div>
    )
  }
}

enum CostType {
  Time = 'time',
  Money = 'money'
}

enum EntityType {
  Item = 'item',
  Villager = 'villager',
  Place = 'place',
  Gift = 'gift'
}

interface ActionData {
  description: string
  costAmount?: number
  costType?: CostType
  waitClass?: WaitClass
  emoji: string
  entityType: EntityType|null
  entityId: number|null
  uniqueDigest: string
  targetCount: number
}

type ActionPillProps = Pick<ActionData, 'costAmount'|'costType'|'emoji'|'waitClass'>

export { ActionPill, type ActionPillProps, type ActionData, WaitClass }
