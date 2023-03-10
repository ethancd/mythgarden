import React from 'react'
import {ActionProps} from "./action";

export default function ActionStem (this: any, { action, targets }: ActionStemProps): JSX.Element {
  function extractGiftId(digest: string) {
    const matchObj = digest.match(/\w*-(\d+)-\d+/)
    const giftIdString = matchObj == null ? null : matchObj[1]
    const giftId = giftIdString == null ? null : parseInt(giftIdString)

    return giftId
  }

  const giftId = extractGiftId(action.uniqueDigest)

  return (
        <li
            className='action action-stem'
            key={action.uniqueDigest}
            data-gift-id={giftId}
            data-villager-names={targets}
        >
            <span className='type'>{action.emoji}</span>&nbsp;
            <span className="description">{action.description}</span>
            <span className="cost">{action.displayCost}</span>
        </li>
  )
}

interface ActionStemProps {
  action: ActionProps
  targets: string[]
}


interface ActionClickData {
  giftId: number | null
  villagerNames: string[]
}

export { ActionStem, type ActionStemProps, type ActionClickData }
