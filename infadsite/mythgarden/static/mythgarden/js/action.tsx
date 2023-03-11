import React from 'react'
import { postAction } from './ajax'

export default function Action (this: any, { description, emoji, displayCost, uniqueDigest }: ActionProps): JSX.Element {
  const postThisAction = postAction.bind(this, uniqueDigest)

  return (
        <li
            onClick={() => { void postThisAction() }}
            className='action'
            key={uniqueDigest}
        >
            <span className='type'>{emoji}</span>&nbsp;
            <span className="description">{description}</span>
            <span className="cost">{displayCost}</span>
        </li>
  )
}

interface ActionProps {
  description: string
  emoji: string
  displayCost: string
  uniqueDigest: string
  targetCount: number
}

export { Action, type ActionProps }
